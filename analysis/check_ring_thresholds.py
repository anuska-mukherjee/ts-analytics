
import duckdb
import pandas as pd


# ---------- DATABASE CONNECTION ----------
con = duckdb.connect("ts.duckdb", read_only=True)


# ---------- LOAD LINK FEATURES AND GROUND TRUTH ----------
data = con.sql("""
    SELECT
        s.user_id,
        COALESCE(s.linked_accounts, 0) AS linked_accounts,
        t.archetype
    FROM int_user_link_stats s
    JOIN read_csv_auto('data/answer_key/users_truth.csv') t
        USING (user_id)
""").df()

con.close()


# ---------- VALIDATION SETUP ----------
# A user is predicted to belong to the coordinated ring
# when linked_accounts is greater than or equal to the threshold.

actual_ring = data["archetype"] == "ring"

thresholds = [1, 2, 3, 5, 10, 20, 30, 39]

results = []


# ---------- THRESHOLD ROBUSTNESS EVALUATION ----------
for threshold in thresholds:

    predicted_ring = data["linked_accounts"] >= threshold

    tp = int((predicted_ring & actual_ring).sum())
    fp = int((predicted_ring & ~actual_ring).sum())
    fn = int((~predicted_ring & actual_ring).sum())
    tn = int((~predicted_ring & ~actual_ring).sum())

    precision = (
        tp / (tp + fp)
        if (tp + fp) > 0
        else 0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn) > 0
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    results.append(
        {
            "threshold": threshold,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
            "precision_pct": round(precision * 100, 2),
            "recall_pct": round(recall * 100, 2),
            "f1_pct": round(f1 * 100, 2),
        }
    )


# ---------- DISPLAY RESULTS ----------
results_df = pd.DataFrame(results)

print("\n========== RING DETECTION THRESHOLD ROBUSTNESS ==========\n")

print(f"Total evaluated users: {len(data):,}")
print(f"Actual coordinated-ring accounts: {int(actual_ring.sum()):,}")

print("\nDetection rule: linked_accounts >= threshold\n")

print(results_df.to_string(index=False))

print("\n==========================================================")


# ---------- SAVE RESULTS ----------
results_df.to_csv(
    "analysis/ring_threshold_robustness.csv",
    index=False,
)

print("\nResults saved to:")
print("analysis/ring_threshold_robustness.csv")
