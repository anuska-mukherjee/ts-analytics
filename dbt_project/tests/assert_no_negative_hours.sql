select report_id
from {{ ref('fct_reports') }}
where hours_to_action < 0