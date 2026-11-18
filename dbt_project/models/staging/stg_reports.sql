select
    report_id,
    reporter_id,
    target_user_id,
    message_id,
    reason,
    cast(created_at as timestamp) as reported_at
from {{ source('raw', 'reports') }}