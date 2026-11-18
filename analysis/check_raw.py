
import duckdb

# Tables expected in the raw dataset
tables = [
    "users",
    "devices",
    "messages",
    "reports",
    "moderators",
    "moderation_actions",
    "appeals",
]

print("\n========== RAW DATA VALIDATION ==========\n")

for table in tables:
    query = f"""
        SELECT COUNT(*) AS total_records
        FROM read_csv_auto('data/raw/{table}.csv')
    """

    result = duckdb.sql(query).fetchall()
    n = result[0][0]

    print(f"{table:20} {n:>10,}")

print("\n========== REPORT REASON DISTRIBUTION ==========\n")

duckdb.sql("""
    SELECT
        reason,
        COUNT(*) AS reports
    FROM read_csv_auto('data/raw/reports.csv')
    GROUP BY reason
    ORDER BY reports DESC
""").show()

print("\n========== VALIDATION COMPLETE ==========\n")
