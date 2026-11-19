with daily as (
    select
        report_date,
        count(*) as reports,
        count(*) filter (where was_reviewed) as reports_reviewed,
        count(*) filter (
            where action_type in ('remove_content', 'warn', 'suspend')
        ) as enforcement_actions,
        median(hours_to_action) as median_hours_to_action,
        quantile_cont(hours_to_action, 0.9) as p90_hours_to_action,
        count(*) filter (where breached_sla) as sla_breaches
    from {{ ref('fct_reports') }}
    group by 1
),

users_to_date as (
    select
        d.report_date,
        count(u.user_id) as registered_users
    from (
        select distinct report_date
        from {{ ref('fct_reports') }}
    ) d
    left join {{ ref('stg_users') }} u
        on cast(u.created_at as date) <= d.report_date
    group by 1
)

select
    d.report_date,
    d.reports,
    u.registered_users,
    round(d.reports * 1000.0 / u.registered_users, 2) as reports_per_1k_users,
    d.reports_reviewed,
    d.enforcement_actions,
    round(d.median_hours_to_action, 1) as median_hours_to_action,
    round(d.p90_hours_to_action, 1) as p90_hours_to_action,
    d.sla_breaches,
    round(
        d.sla_breaches * 1.0 / nullif(d.reports_reviewed, 0), 3
    ) as sla_breach_rate,
    d.report_date >= cast('{{ var("policy_change_date") }}' as date)
        as is_after_policy_change
from daily d
join users_to_date u
    on d.report_date = u.report_date