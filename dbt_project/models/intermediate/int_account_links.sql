
with device_links as (

    select
        a.user_id,
        b.user_id as linked_user_id,
        'device' as link_type,
        a.device_id as link_key

    from {{ ref('stg_devices') }} a

    join {{ ref('stg_devices') }} b
      on a.device_id = b.device_id
     and a.user_id <> b.user_id

),

ip_links as (

    select
        a.user_id,
        b.user_id as linked_user_id,
        'ip' as link_type,
        a.signup_ip_hash as link_key

    from {{ ref('stg_users') }} a

    join {{ ref('stg_users') }} b
      on a.signup_ip_hash = b.signup_ip_hash
     and a.user_id <> b.user_id

)

select * from device_links

union all

select * from ip_links
