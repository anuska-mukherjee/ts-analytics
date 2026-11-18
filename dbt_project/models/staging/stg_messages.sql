select
    message_id,
    sender_id,
    receiver_id,
    cast(sent_at as timestamp) as sent_at,
    "text" as message_text
from {{ source('raw', 'messages') }}