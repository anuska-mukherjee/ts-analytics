
import duckdb
import joblib

K = 500

FEATURES = [
    "account_age_days",
    "linked_accounts",
    "messages_today",
    "messages_7d",
    "reports_today",
    "reports_7d",
    "reports_30d",
]

# Load trained model
model = joblib.load("analysis/risk_model/model.joblib")

# Connect to the project database
con = duckdb.connect("ts.duckdb")

# Retrieve the latest eligible user snapshot
latest = con.sql("""
    select *
    from fct_user_risk_daily
    where snapshot_date = (
        select max(snapshot_date)
        from fct_user_risk_daily
    )
    and enforcement_actions_to_date = 0
""").df()

if latest.empty:
    raise ValueError("No eligible users found in the latest snapshot.")

# Generate risk scores
latest["risk_score"] = model.predict_proba(
    latest[FEATURES]
)[:, 1]

# Rank users by risk score
latest["risk_rank"] = (
    latest["risk_score"]
    .rank(ascending=False, method="first")
    .astype(int)
)

# Flag the top K accounts for review
latest["in_review_queue"] = latest["risk_rank"] <= K

# Save scores into DuckDB
con.register("latest_df", latest)

con.execute("""
    create or replace table ml_risk_scores as
    select * from latest_df
""")

# Display summary
print("\n=== LATEST RISK SCORING ===")

print(
    con.sql("""
        select
            count(*) as total_eligible_users,
            sum(in_review_queue::int) as queued_for_review,
            max(snapshot_date) as snapshot_date
        from ml_risk_scores
    """).fetchall()
)

print("\n=== TOP 10 USERS FOR REVIEW ===")

print(
    con.sql("""
        select
            user_id,
            risk_score,
            risk_rank,
            linked_accounts,
            reports_7d,
            messages_7d
        from ml_risk_scores
        where in_review_queue = true
        order by risk_rank
        limit 10
    """).df().to_string(index=False)
)

con.close()

print("\nSaved risk scores to DuckDB table: ml_risk_scores")
