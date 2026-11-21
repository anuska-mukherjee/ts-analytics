
select
    r.*,
    exists (
        select 1
        from {{ ref('fct_enforcement_actions') }} a
        where a.target_user_id = r.user_id
          and a.action_date > r.snapshot_date
          and a.action_date <= r.snapshot_date + 14
    ) as enforced_next_14d
from {{ ref('fct_user_risk_daily') }} r
where r.enforcement_actions_to_date = 0
  and r.snapshot_date <= cast('{{ var("sim_end_date") }}' as date) - 14
