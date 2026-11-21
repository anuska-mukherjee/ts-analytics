
{{
    config(
        materialized='incremental',
        unique_key=['user_id', 'snapshot_date'],
        incremental_strategy='delete+insert'
    )
}}

with spine as (

    select
        cast(d as date) as snapshot_date

    from generate_series(
        cast('{{ var("sim_start_date") }}' as date),
        cast('{{ var("sim_end_date") }}' as date),
        interval 1 day
    ) as t(d)

    {% if is_incremental() %}

    where cast(d as date) >= (
        select max(snapshot_date)
        from {{ this }}
    ) - 3

    {% endif %}

),

base as (

    select
        u.user_id,
        s.snapshot_date,
        u.created_at

    from {{ ref('stg_users') }} u

    join spine s
        on cast(u.created_at as date) <= s.snapshot_date

),

device_link_events as (

    select
        a.user_id,
        b.user_id as linked_user_id,

        cast(
            greatest(
                a.first_seen_at,
                b.first_seen_at
            ) as date
        ) as link_available_date

    from {{ ref('stg_devices') }} a

    join {{ ref('stg_devices') }} b
        on a.device_id = b.device_id
       and a.user_id <> b.user_id

),

ip_link_events as (

    select
        a.user_id,
        b.user_id as linked_user_id

    from {{ ref('stg_users') }} a

    join {{ ref('stg_users') }} b
        on a.signup_ip_hash = b.signup_ip_hash
       and a.user_id <> b.user_id

),

link_pairs_asof as (

    select distinct
        base.user_id,
        base.snapshot_date,
        d.linked_user_id

    from base

    join device_link_events d
        on base.user_id = d.user_id
       and d.link_available_date <= base.snapshot_date

    union

    select distinct
        base.user_id,
        base.snapshot_date,
        i.linked_user_id

    from base

    join ip_link_events i
        on base.user_id = i.user_id

),

link_feat as (

    select
        user_id,
        snapshot_date,
        count(distinct linked_user_id) as linked_accounts

    from link_pairs_asof

    group by 1, 2

),

msgs as (

    select
        sender_id as user_id,
        cast(sent_at as date) as d,
        count(*) as n

    from {{ ref('stg_messages') }}

    group by 1, 2

),

reps as (

    select
        target_user_id as user_id,
        cast(reported_at as date) as d,
        count(*) as n

    from {{ ref('stg_reports') }}

    group by 1, 2

),

acts as (

    select
        target_user_id as user_id,
        cast(actioned_at as date) as d,
        count(*) as n

    from {{ ref('int_report_to_action') }}

    where action_type <> 'no_action'

    group by 1, 2

),

msg_feat as (

    select
        b.user_id,
        b.snapshot_date,

        coalesce(
            sum(m.n) filter (
                where m.d = b.snapshot_date
            ),
            0
        ) as messages_today,

        coalesce(
            sum(m.n) filter (
                where m.d >= b.snapshot_date - 6
            ),
            0
        ) as messages_7d

    from base b

    left join msgs m
        on m.user_id = b.user_id
       and m.d between b.snapshot_date - 6
                   and b.snapshot_date

    group by 1, 2

),

rep_feat as (

    select
        b.user_id,
        b.snapshot_date,

        coalesce(
            sum(r.n) filter (
                where r.d = b.snapshot_date
            ),
            0
        ) as reports_today,

        coalesce(
            sum(r.n) filter (
                where r.d >= b.snapshot_date - 6
            ),
            0
        ) as reports_7d,

        coalesce(
            sum(r.n),
            0
        ) as reports_30d

    from base b

    left join reps r
        on r.user_id = b.user_id
       and r.d between b.snapshot_date - 29
                   and b.snapshot_date

    group by 1, 2

),

act_feat as (

    select
        b.user_id,
        b.snapshot_date,

        coalesce(
            sum(a.n),
            0
        ) as enforcement_actions_to_date

    from base b

    left join acts a
        on a.user_id = b.user_id
       and a.d <= b.snapshot_date

    group by 1, 2

)

select
    b.user_id,
    b.snapshot_date,

    date_diff(
        'day',
        cast(b.created_at as date),
        b.snapshot_date
    ) as account_age_days,

    coalesce(
        l.linked_accounts,
        0
    ) as linked_accounts,

    m.messages_today,
    m.messages_7d,

    r.reports_today,
    r.reports_7d,
    r.reports_30d,

    a.enforcement_actions_to_date

from base b

left join link_feat l
    using (user_id, snapshot_date)

join msg_feat m
    using (user_id, snapshot_date)

join rep_feat r
    using (user_id, snapshot_date)

join act_feat a
    using (user_id, snapshot_date)
