with actions as (
    select
        moderator_id,
        count(*) as enforcement_actions,
        count(*) filter (where was_appealed) as appeals,
        count(*) filter (where was_overturned) as overturned
    from {{ ref('fct_enforcement_actions') }}
    group by 1
),

reviewed as (
    select
        moderator_id,
        count(*) as reports_reviewed,
        median(hours_to_action) as median_hours_to_action
    from {{ ref('fct_reports') }}
    where was_reviewed
    group by 1
),

base as (
    select
        m.moderator_id,
        m.team,
        r.reports_reviewed,
        a.enforcement_actions,
        round(a.enforcement_actions * 1.0 / r.reports_reviewed, 3) as enforcement_rate,
        a.appeals,
        a.overturned,
        round(a.overturned * 1.0 / a.enforcement_actions, 3) as overturn_rate,
        round(r.median_hours_to_action, 1) as median_hours_to_action
    from {{ ref('dim_moderators') }} m
    join reviewed r on m.moderator_id = r.moderator_id
    join actions a on m.moderator_id = a.moderator_id
),

team_median as (
    select median(overturn_rate) as median_overturn_rate
    from base
)

select
    b.*,
    t.median_overturn_rate,
    b.overturn_rate > 2 * t.median_overturn_rate as is_overturn_outlier
from base b
cross join team_median t