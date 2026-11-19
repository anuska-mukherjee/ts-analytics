select
    moderator_id,
    team,
    hired_at
from {{ ref('stg_moderators') }}