
# Trust & Safety Analytics — Key Findings

## Executive summary

- **Coordinated abuse detection:** The account-linking pipeline identified all 40 planted ring accounts, with no false positives in this synthetic dataset.
- **Moderator quality:** Moderator 7 had a 9.40% overturn rate, compared with 2.31% across all other moderators pooled.
- **Operational performance:** Mean daily median action time increased by approximately 50.6% after the simulated policy-change date, while the report rate per 1,000 messages remained broadly stable.

## Project overview

This project uses synthetic Trust & Safety platform data to build an analytics pipeline with dbt and DuckDB.

The pipeline transforms raw user, device, message, report, moderation-action, moderator, and appeal data into analytical models and KPI marts.

The analysis focuses on three areas:

1. Detecting coordinated accounts through shared device and signup-IP signals.
2. Evaluating moderation quality through appeal overturn rates.
3. Monitoring reporting volumes, exposure-normalised reporting rates, and moderation response times.

The analysis period is July–September 2026. The policy-change comparison uses August 15, 2026 as the before/after boundary.

## Finding 1 — Coordinated account detection

The account-linking pipeline uses shared device identifiers and hashed signup IPs to identify potentially related accounts.

### Results

| Metric | Result |
|---|---:|
| Planted ring accounts | 40 |
| Ring accounts correctly flagged | 40 |
| False positives | 0 |
| False negatives | 0 |
| True negatives | 19,960 |

On this synthetic dataset:

- Precision: 100%
- Recall: 100%
- False-positive rate: 0%

The pipeline successfully recovered the planted ring.

### Interpretation and limitations

This is a controlled validation against deliberately planted patterns, not evidence of equivalent performance in production.

Shared devices and IP addresses can be legitimate. Examples include households, universities, workplaces, mobile carriers, and public networks.

A production detection system should combine multiple independent signals, use risk scoring rather than automatic enforcement, and include human review.

## Finding 2 — Policy-period reporting and operational performance

A comparison of activity before and after August 15 initially showed a substantial increase in daily report volume.

However, raw report volume alone does not establish that users became more likely to report content. Platform activity also increased during the simulation.

### Reporting volume and exposure

| Metric | Before Aug 15 | After Aug 15 |
|---|---:|---:|
| Average daily reports | 91 | 213 |
| Messages | 51,529 | 124,603 |
| Reports per 1,000 messages | 80.36 | 79.93 |

Daily report volume increased by approximately 134%.

However, after normalising by message volume, the reporting rate decreased by approximately 0.54%.

**Interpretation:** The increase in raw reports is largely consistent with platform activity growth. The exposure-normalised metric does not show an increase in reporting propensity after the policy-change date.

### Moderation response time

| Metric | Before Aug 15 | After Aug 15 |
|---|---:|---:|
| Mean of daily median action time | 7.9 hours | 11.9 hours |

The mean daily median action time increased by approximately 50.6%.

**Interpretation:** The simulated post-change period shows a meaningful slowdown in moderation response time. This could indicate increased operational pressure or a change in queue processing efficiency.

This is a before/after comparison on synthetic data, not proof that the policy change caused the slowdown.

### Analytical takeaway

Choosing the correct denominator matters.

Registered-user counts and raw report totals can be misleading when platform activity changes over time. Message volume provides a more direct exposure denominator for this reporting-rate comparison.

## Finding 3 — Moderator quality and appeal overturns

Moderator 7 stands out when comparing overturned enforcement actions against all other moderators pooled.

### Results

| Metric | Moderator 7 | Other moderators |
|---|---:|---:|
| Enforcement actions | 1,390 | 9,684 |
| Overturned actions | 130 | 224 |
| Overturn rate | 9.40% | 2.31% |

The overturn rate is calculated as:

`Overturned enforcement actions / Total enforcement actions`

Moderator 7's overturn rate is approximately 4.1 times the pooled rate of the other moderators.

The absolute difference is approximately 7.09 percentage points.

Moderator 7's approximate 95% confidence interval is 7.87%–10.93%.

The difference is approximately 8.89 combined standard errors, indicating a strong statistical signal in this dataset.

### Interpretation

The difference warrants further investigation, particularly because the sample includes 1,390 enforcement actions for Moderator 7.

However, an elevated overturn rate does not automatically establish poor moderator performance.

Potential explanations include:

- Different policy-category or case complexity distributions.
- Unequal assignment of difficult or high-risk cases.
- Differences in enforcement thresholds.
- Inconsistent policy interpretation or training.

### Recommended investigation

Compare moderators by policy category, enforcement type, case severity, and workload.

Review a sample of overturned cases to identify recurring decision patterns before drawing conclusions about individual performance.

## Planted patterns vs. recovered results

| Planted or simulated pattern | Pipeline result |
|---|---|
| Ring of 40 linked accounts | All 40 recovered; zero false positives in this dataset |
| Moderator with elevated overturn rate | Moderator 7: 9.40% vs. 2.31% pooled for other moderators |
| 1.5x slower moderation queue after the simulated change | Mean daily median action time increased from 7.9 to 11.9 hours (+50.6%) |
| Increased reporting after the simulated change | Not supported by exposure-normalised results: 80.36 to 79.93 reports per 1,000 messages (-0.54%) |

The reporting-rate result is intentionally retained as a discrepancy rather than presented as a successful recovery. The generator's intended pattern and the observed data should be reconciled before claiming that reporting propensity increased.

## Limitations

- The dataset is synthetic and contains deliberately planted patterns.
- Detection performance against planted ground truth does not establish real-world generalisation.
- Shared IPs and devices can create legitimate account relationships.
- Before/after comparisons do not establish causality.
- Message volume is used as the exposure denominator for reporting rates; other denominators may be appropriate for different product questions.
- Moderator overturn rates should be interpreted alongside case mix, policy categories, and assignment patterns.
- The confidence interval reported for Moderator 7 is an approximate normal (Wald) interval.

## Recommended next steps

### 1. Build an account risk-scoring model

Combine account-link signals, reporting history, enforcement history, and behavioural patterns into a risk score.

Evaluate precision, recall, false-positive rates, and performance at different review thresholds.

### 2. Experiment with LLM-assisted report triage

Build an LLM-assisted triage prototype that classifies incoming reports, extracts relevant evidence, and recommends a policy category for human review.

Evaluate classification quality, reviewer agreement, processing time, and escalation accuracy.

The model should assist human reviewers rather than make autonomous enforcement decisions.

### 3. Improve moderator quality monitoring

Add case-mix-adjusted moderator comparisons, category-level overturn rates, and minimum sample-size requirements.

### 4. Extend operational monitoring

Add rolling averages, anomaly detection, queue backlog, and SLA breach trends to identify emerging operational issues.

---

## Tools and technologies

- SQL
- dbt Core
- DuckDB
- Python
- pandas
- Synthetic data generation
- Data quality tests
- GitHub
