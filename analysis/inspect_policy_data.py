
import duckdb

con = duckdb.connect("ts.duckdb", read_only=True)

for table in ["stg_messages", "stg_reports"]:
    print(f"\n========== {table}: COLUMNS ==========")
    print(con.sql(f"DESCRIBE {table}").df().to_string(index=False))

print("\n========== MESSAGE SAMPLE ==========")
con.sql("SELECT * FROM stg_messages LIMIT 5").show()

print("\n========== REPORT REASONS ==========")
con.sql("""
    SELECT reason, COUNT(*) AS reports
    FROM stg_reports
    GROUP BY reason
    ORDER BY reports DESC
""").show()

print("\n========== REPORT REASONS BY PERIOD ==========")
con.sql("""
    SELECT
        CASE
            WHEN CAST(reported_at AS DATE) >= DATE '2026-08-15'
            THEN 'After'
            ELSE 'Before'
        END AS period,
        reason,
        COUNT(*) AS reports
    FROM stg_reports
    GROUP BY 1, 2
    ORDER BY 1, 3 DESC
""").show()

con.close()
