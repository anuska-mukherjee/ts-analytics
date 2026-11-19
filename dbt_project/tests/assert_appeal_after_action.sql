select appeal_id
from {{ ref('int_report_to_action') }}
where appealed_at < actioned_at