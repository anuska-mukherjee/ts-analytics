
import json
from pathlib import Path

import duckdb
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score

OUT = Path("analysis/risk_model")
DOCS = Path("docs")
OUT.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(exist_ok=True)

K = 500
KS = [100, 250, 500, 1000, 2000, 4000]

REVIEW_COST, MISS_COST = 1, 10
LABEL = "enforced_next_14d"

FEATURES = [
    "account_age_days",
    "linked_accounts",
    "messages_today",
    "messages_7d",
    "reports_today",
    "reports_7d",
    "reports_30d",
]

# More reports/messages/links should never LOWER risk.
MONOTONIC = [0, 1, 1, 1, 1, 1, 1]

rng = np.random.default_rng(42)

# ---------- LOAD ----------
con = duckdb.connect("ts.duckdb", read_only=True)

df = con.sql(
    "select * from ml_risk_training_set"
).df()

con.close()

df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
df[LABEL] = df[LABEL].astype(int)

# ---------- TIME-BASED SPLIT ----------
train = df[df.snapshot_date <= "2026-08-01"].copy()

val = df[
    df.snapshot_date.between("2026-08-16", "2026-08-31")
].copy()

test = df[
    df.snapshot_date.between("2026-09-01", "2026-09-16")
].copy()

for name, d in [
    ("train", train),
    ("val", val),
    ("test", test)
]:
    print(
        f"{name:5} rows={len(d):>9,}  "
        f"bad-rate={d[LABEL].mean():.3f}"
    )

# ---------- MODEL ----------
model = HistGradientBoostingClassifier(
    max_depth=4,
    learning_rate=0.1,
    max_iter=200,
    monotonic_cst=MONOTONIC,
    random_state=42,
)

model.fit(train[FEATURES], train[LABEL])

# ---------- TRANSPARENT RULES BASELINE ----------
def rules_score(d):
    s = (
        2 * np.minimum(d.reports_7d, 5)
        + 5 * (d.linked_accounts >= 5)
        + 3 * (d.messages_today >= 40)
        + 1 * (d.reports_30d >= 3)
    ).astype(float)

    return s + rng.random(len(d)) * 0.01


for d in (val, test):
    d["score"] = model.predict_proba(d[FEATURES])[:, 1]
    d["rules"] = rules_score(d)

# ---------- CAPACITY-CONSTRAINED EVALUATION ----------
def capacity_metrics(d, col, k):
    rows = []

    for _, g in d.groupby("snapshot_date"):
        top = g.nlargest(k, col)

        rows.append((
            top[LABEL].sum(),
            g[LABEL].sum(),
            len(top),
            len(g),
        ))

    tp, pos, n_top, n = np.array(rows, dtype=float).T

    return {
        "k": k,
        "precision": float(np.mean(tp / n_top)),
        "recall": float(np.mean(tp / pos)),
        "base_rate": float(np.mean(pos / n)),
        "avg_caught": float(tp.mean()),
        "avg_bad_per_day": float(pos.mean()),
    }


sweep = {
    col: [
        capacity_metrics(test, col, k)
        for k in KS
    ]
    for col in ("score", "rules")
}

# ---------- RESULTS ----------
results = {
    "capacity_k": K,
    "model": {},
    "rules": {},
}

print("\n=== Ranking quality (higher is better) ===")

for name, d in [
    ("val", val),
    ("test", test),
]:
    for col, label in [
        ("score", "model"),
        ("rules", "rules"),
    ]:
        ap = average_precision_score(d[LABEL], d[col])
        auc = roc_auc_score(d[LABEL], d[col])

        results[label][f"{name}_pr_auc"] = float(ap)
        results[label][f"{name}_roc_auc"] = float(auc)

        print(
            f"{name:4} {label:6} "
            f"PR-AUC={ap:.3f}  ROC-AUC={auc:.3f}"
        )

# ---------- CAPACITY RESULTS ----------
print(
    f"\n=== Test set, team can review {K} accounts/day ==="
)

table = []

for col, label in [
    ("score", "model"),
    ("rules", "rules"),
]:
    m = next(
        x for x in sweep[col]
        if x["k"] == K
    )

    results[label]["at_capacity"] = m

    table.append({
        "approach": label,
        "precision@K": round(m["precision"], 3),
        "recall@K": round(m["recall"], 3),
        "lift_vs_random": round(
            m["precision"] / m["base_rate"], 2
        ),
        "bad_caught/day": round(m["avg_caught"], 1),
    })

print(pd.DataFrame(table).to_string(index=False))

print(
    f"(random review would catch "
    f"{sweep['score'][0]['base_rate']:.1%} precision)"
)

# ---------- COST VIEW ----------
print(
    "\n=== Daily cost = reviews + 10 x missed bad accounts "
    "(lower is better) ==="
)

cost_rows = []

for col, label in [
    ("score", "model"),
    ("rules", "rules"),
]:
    for m in sweep[col]:
        cost = (
            REVIEW_COST * m["k"]
            + MISS_COST * (
                m["avg_bad_per_day"] - m["avg_caught"]
            )
        )

        cost_rows.append({
            "approach": label,
            "K": m["k"],
            "daily_cost": round(cost),
        })

cost_df = pd.DataFrame(cost_rows).pivot(
    index="K",
    columns="approach",
    values="daily_cost",
)

print(cost_df.to_string())

results["cheapest_k"] = {
    c: int(cost_df[c].idxmin())
    for c in cost_df.columns
}

# ---------- CHART ----------
plt.figure(figsize=(7, 4.5))

for col, label in [
    ("score", "Gradient boosting"),
    ("rules", "Rules baseline"),
]:
    plt.plot(
        KS,
        [m["recall"] for m in sweep[col]],
        marker="o",
        label=label,
    )

plt.axvline(K, ls="--", color="grey", lw=1)
plt.xscale("log")

plt.xlabel("Accounts reviewed per day (capacity)")
plt.ylabel("Share of soon-to-be-enforced users caught")
plt.title("Risk model vs rules baseline (test period)")

plt.legend()
plt.grid(alpha=0.3)

plt.savefig(
    DOCS / "risk_model_recall_at_k.png",
    dpi=150,
    bbox_inches="tight",
)

# ---------- SAVE ----------
with open(OUT / "results.json", "w") as f:
    json.dump(results, f, indent=2)

joblib.dump(
    model,
    OUT / "model.joblib",
)

test.to_csv(
    OUT / "test_scored.csv.gz",
    index=False,
)

print(
    "\nSaved: results.json, model.joblib, "
    "test_scored.csv.gz, docs/risk_model_recall_at_k.png"
)
