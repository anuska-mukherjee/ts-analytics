select
    action_id,
    report_id,
    moderator_id,
    target_user_id,
    action_type,
    actioned_at,
    cast(actioned_at as date) as action_date,
    appeal_id is not null as was_appealed,
    appeal_outcome,
    coalesce(appeal_outcome = 'overturned', false) as was_overturned
from {{ ref('int_report_to_action') }}
where action_id is not null
  and action_type <> 'no_action'