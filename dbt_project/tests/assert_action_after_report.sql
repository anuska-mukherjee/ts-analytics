select report_id
from {{ ref('int_report_to_action') }}
where actioned_at < reported_at