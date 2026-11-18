select
    user_id,
    md5(lower(email)) as email_hash,
    md5(signup_ip) as signup_ip_hash,
    country,
    cast(created_at as timestamp) as created_at
from {{ source('raw', 'users') }}