with severity as (
    select
        target_user_id as user_id,
        max(
            case action_type
                when 'suspend' then 3
                when 'remove_content' then 2
                when 'warn' then 1
            end
        ) as max_severity
    from {{ ref('int_report_to_action') }}
    where action_type <> 'no_action'
      and actioned_at <= cast('{{ var("as_of_date") }}' as timestamp)
    group by 1
)

select
    u.user_id,
    case coalesce(s.max_severity, 0)
        when 3 then 'suspended'
        when 2 then 'content_removed'
        when 1 then 'warned'
        else 'active'
    end as status
from {{ ref('stg_users') }} u
left join severity s
    on u.user_id = s.user_id