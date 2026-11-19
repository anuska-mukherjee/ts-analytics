with reports_received as (
    select
        target_user_id as user_id,
        count(*) as reports_received,
        min(reported_at) as first_reported_at
    from {{ ref('fct_reports') }}
    group by 1
),

enforcement as (
    select
        target_user_id as user_id,
        count(*) as enforcement_actions
    from {{ ref('fct_enforcement_actions') }}
    group by 1
)

select
    u.user_id,
    u.country,
    u.created_at,
    s.linked_accounts,
    s.device_linked_accounts,
    s.ip_linked_accounts,
    s.linked_accounts >= 5 as is_in_linked_cluster,
    coalesce(rr.reports_received, 0) as reports_received,
    rr.first_reported_at,
    coalesce(e.enforcement_actions, 0) as enforcement_actions
from {{ ref('stg_users') }} u
join {{ ref('int_user_link_stats') }} s
    on u.user_id = s.user_id
left join reports_received rr
    on u.user_id = rr.user_id
left join enforcement e
    on u.user_id = e.user_id