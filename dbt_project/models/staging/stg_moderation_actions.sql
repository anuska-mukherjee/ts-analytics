select
    action_id,
    report_id,
    moderator_id,
    action_type,
    cast(actioned_at as timestamp) as actioned_at
from {{ source('raw', 'moderation_actions') }}