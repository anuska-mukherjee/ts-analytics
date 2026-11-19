
import duckdb

con = duckdb.connect("ts.duckdb", read_only=True)

print("1) Snapshot: current status counts and users with history")

con.sql("""
    select
        status,
        count(*) filter (
            where dbt_valid_to is null
        ) as current_users,
        count(*) as total_rows
    from snap_user_status
    group by 1
    order by 2 desc
""").show()

con.sql("""
    select count(*) as users_with_status_changes
    from (
        select user_id
        from snap_user_status
        group by 1
        having count(*) > 1
    )
""").show()

print("2) Risk table: date range and row count")

con.sql("""
    select
        min(snapshot_date) as start_date,
        max(snapshot_date) as end_date,
        count(*) as rows
    from fct_user_risk_daily
""").show()

print("3) Who looks riskiest on the last day?")

con.sql("""
    select
        t.archetype,
        count(*) as users,
        round(avg(r.reports_30d), 2) as avg_reports_30d,
        round(avg(r.messages_7d), 1) as avg_messages_7d,
        round(avg(r.linked_accounts), 1) as avg_linked_accounts
    from fct_user_risk_daily r
    join read_csv_auto(
        'data/answer_key/users_truth.csv'
    ) t using (user_id)
    where r.snapshot_date = (
        select max(snapshot_date)
        from fct_user_risk_daily
    )
    group by 1
    order by avg_reports_30d desc
""").show()
