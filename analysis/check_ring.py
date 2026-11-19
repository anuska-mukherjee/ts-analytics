
import duckdb

con = duckdb.connect("ts.duckdb", read_only=True)

print("\n========== LINK COUNTS BY HIDDEN USER TYPE ==========\n")

con.sql("""
    SELECT
        t.archetype,
        COUNT(*) AS users,
        ROUND(AVG(s.linked_accounts), 1) AS avg_linked_accounts,
        MAX(s.linked_accounts) AS max_linked_accounts
    FROM int_user_link_stats s
    JOIN read_csv_auto('data/answer_key/users_truth.csv') t
        USING (user_id)
    GROUP BY t.archetype
    ORDER BY avg_linked_accounts DESC
""").show()

print("\n========== TOP 5 REPORT-HEAVY USERS ==========\n")

con.sql("""
    SELECT
        target_user_id,
        MAX(prior_reports_30d) AS peak_30d_reports
    FROM int_user_report_history
    GROUP BY target_user_id
    ORDER BY peak_30d_reports DESC
    LIMIT 5
""").show()

con.close()
