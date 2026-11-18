select
    user_id,
    device_id,
    min(cast(first_seen_at as timestamp)) as first_seen_at
from {{ source('raw', 'devices') }}
group by user_id, device_id