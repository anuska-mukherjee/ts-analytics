
select
    report_id,
    target_user_id,
    reported_at,

    count(*) over (
        partition by target_user_id
        order by reported_at
        range between interval 7 days preceding
        and current row
    ) - 1 as prior_reports_7d,

    count(*) over (
        partition by target_user_id
        order by reported_at
        range between interval 30 days preceding
        and current row
    ) - 1 as prior_reports_30d

from {{ ref('stg_reports') }}
