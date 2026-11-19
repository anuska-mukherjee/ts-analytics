
select
    u.user_id,

    count(distinct l.linked_user_id)
        as linked_accounts,

    count(
        distinct case
            when l.link_type = 'device'
            then l.linked_user_id
        end
    ) as device_linked_accounts,

    count(
        distinct case
            when l.link_type = 'ip'
            then l.linked_user_id
        end
    ) as ip_linked_accounts

from {{ ref('stg_users') }} u

left join {{ ref('int_account_links') }} l
    on u.user_id = l.user_id

group by u.user_id