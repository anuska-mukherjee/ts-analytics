# Trust & Safety Analytics - Key Findings

## Project overview

Built a Trust & Safety analytics pipeline using Python, DuckDB, SQL and dbt to analyse synthetic user reports, moderation decisions, appeals, moderator performance and account-linkage signals.

Dataset: 20,000 synthetic users.

## Finding 1: Moderator quality anomaly

Moderator 7 reviewed 1,390 reports and recorded an appeal overturn rate of 9.4%, compared with 3.2%–3.8% among the next four highest moderators.

**Business implication:** Investigate decision consistency, case mix and policy interpretation. Review overturned cases to identify training or policy-calibration opportunities.

## Finding 2: Policy-change impact on moderation operations

Comparing the periods before and after the simulated policy change:

- Average daily reports increased from 91 to 213 (+134.1%).
- Reports per 1,000 registered users decreased from 30.39 to 13.68 (-55.0%).
- Average daily median action time increased from 7.9 to 11.9 hours (+50.6%).

**Business implication:** Raw report volume and user-normalised reporting rates tell different stories. Moderation capacity and queue performance should be monitored alongside platform growth.

*Note: This is a before/after comparison on synthetic data, not evidence that a real policy change caused these movements.*

## Finding 3: Account-linkage risk signal

The 40 users flagged as members of linked-account clusters had:

- 12.75 average reports received, versus 0.68 for other users.
- 11.25 average enforcement actions, versus 0.53 for other users.

**Business implication:** Shared-device and shared-IP relationships can help prioritise coordinated-abuse investigations. They should be combined with behavioural evidence and human review.

## Technical implementation

- Python for synthetic data generation and analysis.
- DuckDB for analytical storage and SQL execution.
- dbt for staging, intermediate transformations, fact tables, dimensions and KPI marts.
- SQL window functions, joins, aggregations and data quality tests.

## Limitations

- The dataset is synthetic and contains deliberately planted patterns.
- Account linkage is a risk signal, not proof of coordinated abuse.
- Moderator outlier detection should account for case mix and appeal sample sizes.
- Before/after comparisons do not establish causation.
