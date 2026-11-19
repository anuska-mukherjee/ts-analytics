select
    r.report_id,
    r.reporter_id,
    r.target_user_id,
    r.message_id,
    r.reason,
    r.reported_at,
    cast(r.reported_at as date) as report_date,
    r.was_reviewed,
    r.action_id,
    r.moderator_id,
    r.action_type,
    r.actioned_at,
    r.hours_to_action,
    r.hours_to_action > {{ var('sla_hours') }} as breached_sla,
    r.appeal_id is not null as was_appealed,
    r.appeal_outcome,
    h.prior_reports_7d,
    h.prior_reports_30d
from {{ ref('int_report_to_action') }} r
join {{ ref('int_user_report_history') }} h
  on r.report_id = h.report_id