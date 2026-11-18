select
    moderator_id,
    team,
    cast(hired_at as timestamp) as hired_at
from {{ source('raw', 'moderators') }}