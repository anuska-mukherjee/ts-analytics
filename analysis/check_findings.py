
import duckdb

con = duckdb.connect("ts.duckdb", read_only=True)

print("1) Messages per week (is the platform growing?):")
con.sql("""
    select
        date_trunc('week', cast(sent_at as date)) as week,
        count(*) as messages
    from stg_messages
    group by 1
    order by 1
""").show()

print("2) Reports per 1k messages, by message sent date:")
con.sql("""
    with m as (
        select
            message_id,
            cast(sent_at as date) >= date '2026-08-15'
                as after_policy
        from stg_messages
    )
    select
        m.after_policy,
        count(*) as messages,
        count(r.report_id) as reports,
        round(
            count(r.report_id) * 1000.0 / count(*), 2
        ) as reports_per_1k_messages
    from m
    left join stg_reports r using (message_id)
    group by 1
    order by 1
""").show()

print("3) Linked-cluster flag vs the answer key:")
con.sql("""
    select
        t.archetype = 'ring' as truly_ring,
        u.is_in_linked_cluster as flagged,
        count(*) as users
    from dim_users u
    join read_csv_auto(
        'data/answer_key/users_truth.csv'
    ) t using (user_id)
    group by 1, 2
    order by 1, 2
""").show()
