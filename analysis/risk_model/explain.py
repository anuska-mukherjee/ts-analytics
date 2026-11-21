
import duckdb
import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

K = 500
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

# Load trained model and test predictions
model = joblib.load("analysis/risk_model/model.joblib")

test = pd.read_csv(
    "analysis/risk_model/test_scored.csv.gz",
    parse_dates=["snapshot_date"]
)

# Load local synthetic ground truth and country data
con = duckdb.connect("ts.duckdb", read_only=True)

truth = con.sql("""
    select *
    from read_csv_auto('data/answer_key/users_truth.csv')
""").df()

users = con.sql("""
    select user_id, country
    from stg_users
""").df()

con.close()

# Attach archetype and country to test predictions
test = test.merge(truth, on="user_id")
test = test.merge(users, on="user_id")

# --------------------------------------------------
# 1. Permutation feature importance
# --------------------------------------------------

print("\n=== PERMUTATION FEATURE IMPORTANCE ===")

sample = test.sample(30_000, random_state=42)

imp = permutation_importance(
    model,
    sample[FEATURES],
    sample[LABEL],
    scoring="average_precision",
    n_repeats=3,
    random_state=42,
)

importance = pd.DataFrame({
    "feature": FEATURES,
    "pr_auc_drop": imp.importances_mean,
    "std": imp.importances_std,
}).sort_values("pr_auc_drop", ascending=False)

print(importance.round(4).to_string(index=False))

# --------------------------------------------------
# 2. Recall at K by user archetype
# --------------------------------------------------

print("\n=== RECALL AT K=500 BY ARCHETYPE ===")

for col in ("score", "rules"):
    test[f"flag_{col}"] = (
        test.groupby("snapshot_date")[col]
        .rank(ascending=False, method="first") <= K
    )

pos = test[test[LABEL] == 1].copy()

archetype_recall = (
    pos.groupby("archetype")[["flag_score", "flag_rules"]]
    .mean()
    .round(3)
)

print(archetype_recall.to_string())

users_enforced = (
    pos.groupby("archetype")["user_id"]
    .nunique()
)

print("\nUnique users enforced within 14 days by archetype:")
print(users_enforced.to_string())

# --------------------------------------------------
# 3. Country-level review flags among normal users
#    who were not enforced in the next 14 days
# --------------------------------------------------

print("\n=== COUNTRY REVIEW-FLAG RATE ===")

clean = test[
    (test["archetype"] == "normal")
    & (test[LABEL] == 0)
].copy()

by_country = (
    clean.groupby("country")["flag_score"]
    .mean()
    .round(4)
    .sort_values(ascending=False)
)

print("\nHighest review-flag rates:")
print(by_country.head(10).to_string())

print("\nLowest review-flag rates:")
print(by_country.tail(10).to_string())

if len(by_country) > 0 and by_country.min() > 0:
    ratio = by_country.max() / by_country.min()
    print(f"\nHighest-to-lowest country rate ratio: {ratio:.2f}x")
else:
    print("\nCountry rate ratio unavailable because a rate is zero or no groups exist.")
