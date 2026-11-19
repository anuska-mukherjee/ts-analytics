
import duckdb

con = duckdb.connect("ts.duckdb", read_only=True)

print("1) Moderator quality (top 5 by overturn rate):")
con.sql("""
    select
        moderator_id,
        reports_reviewed,
        enforcement_rate,
        overturn_rate,
        is_overturn_outlier
    from mart_moderator_quality
    order by overturn_rate desc
    limit 5
""").show()

print("2) Reports per day, before vs after the policy change:")
con.sql("""
    select
        is_after_policy_change,
        round(avg(reports), 0) as avg_reports_per_day,
        round(avg(reports_per_1k_users), 2) as avg_reports_per_1k_users,
        round(avg(median_hours_to_action), 1) as avg_median_hours_to_action
    from mart_ts_kpis_daily
    group by 1
    order by 1
""").show()

print("3) Linked-cluster users:")
con.sql("""
    select
        u.is_in_linked_cluster,
        count(*) as users,
        round(avg(u.reports_received), 2) as avg_reports_received,
        round(avg(u.enforcement_actions), 2) as avg_enforcement_actions
    from dim_users u
    group by 1
    order by 1
""").show()
