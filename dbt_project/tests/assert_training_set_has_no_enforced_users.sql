
select
    user_id,
    snapshot_date
from {{ ref('ml_risk_training_set') }}
where enforcement_actions_to_date > 0
