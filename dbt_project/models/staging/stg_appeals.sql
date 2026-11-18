select
    appeal_id,
    action_id,
    user_id,
    outcome,
    cast(created_at as timestamp) as appealed_at,
    cast(resolved_at as timestamp) as resolved_at
from {{ source('raw', 'appeals') }}