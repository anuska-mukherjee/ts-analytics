
select
    r.report_id,
    r.reporter_id,
    r.target_user_id,
    r.message_id,
    r.reason,
    r.reported_at,

    a.action_id,
    a.moderator_id,
    a.action_type,
    a.actioned_at,

    ap.appeal_id,
    ap.outcome as appeal_outcome,
    ap.appealed_at,
    ap.resolved_at,

    a.action_id is not null as was_reviewed,

    date_diff(
        'minute',
        r.reported_at,
        a.actioned_at
    ) / 60.0 as hours_to_action

from {{ ref('stg_reports') }} r

left join {{ ref('stg_moderation_actions') }} a
    on r.report_id = a.report_id

left join {{ ref('stg_appeals') }} ap
    on a.action_id = ap.action_id
