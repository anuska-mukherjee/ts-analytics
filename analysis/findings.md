
# Trust & Safety Analytics — Key Findings

## Executive summary

- **Coordinated abuse detection:** The account-linking pipeline identified all 40 planted ring accounts, with no false positives in this synthetic dataset.
- **Moderator quality:** Moderator 7 had a 9.40% overturn rate, compared with 2.31% across all other moderators pooled.
- **Reporting patterns:** Overall reports per 1,000 messages remained broadly stable (-0.54%), but report composition shifted sharply after August 15: harassment rose from 17.84% to 53.82% of reports (+35.97 percentage points), while spam fell from 67.11% to 39.09%.
- **Operational performance:** Mean daily median action time increased by approximately 50.6% after the simulated policy-change date, from 7.9 to 11.9 hours.
- **Risk prediction:** A temporal risk model achieved a test PR-AUC of 0.118, compared with 0.065 for the rules baseline. At a review capacity of 500 accounts per day, the model achieved 22.7% recall and 7.2% precision.

## Project overview

This project uses synthetic Trust & Safety platform data to build an analytics pipeline with dbt and DuckDB.

The pipeline transforms raw user, device, message, report, moderation-action, moderator, and appeal data into analytical models and KPI marts.

The analysis focuses on four areas:

1. Detecting coordinated accounts through shared device and signup-IP signals.
2. Evaluating moderation quality through appeal overturn rates.
3. Monitoring reporting volumes, report-category composition, and moderation response times.
4. Predicting future enforcement risk to support prioritisation of human review.

The analysis period is July–September 2026. The policy-change comparison uses August 15, 2026 as the before/after boundary.

---

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

---

## Finding 2 — Policy-period reporting and operational performance

A comparison of platform activity before and after August 15, 2026 showed a substantial increase in daily report volume.

However, raw report volume alone does not establish that users became more likely to report content. Platform activity also increased, and the composition of report categories changed substantially.

### Reporting volume and exposure

| Metric | Before Aug 15 | After Aug 15 |
|---|---:|---:|
| Average daily reports | 91 | 213 |
| Messages | 51,529 | 124,603 |
| Reports per 1,000 messages | 80.36 | 79.93 |

Daily report volume increased by approximately 134%.

The exposure-normalised reporting rate decreased slightly, from 80.36 to 79.93 reports per 1,000 messages (-0.54%).

### Report-category mix shift

The composition of submitted reports changed substantially across the two periods.

| Category | Before reports | After reports | Before share | After share | Change |
|---|---:|---:|---:|---:|---:|
| Spam | 2,753 | 3,909 | 67.11% | 39.09% | -28.02 pp |
| Harassment | 732 | 5,381 | 17.84% | 53.82% | +35.97 pp |
| Scam | 617 | 709 | 15.04% | 7.09% | -7.95 pp |
| **Total** | **4,102** | **9,999** | **100%** | **100%** | |

Harassment became the largest report category after August 15, increasing from 17.84% to 53.82% of all reports.

Spam's share declined from 67.11% to 39.09%, while scam's share declined from 15.04% to 7.09%.

**Interpretation:** The post-change period is characterised by a substantial shift in report-category composition, particularly toward harassment. The overall exposure-normalised reporting rate remained broadly stable, but this aggregate metric masks the change in the types of reports being submitted.

The available data does not contain policy categories for individual messages. Therefore, category-specific reporting rates cannot be calculated, and this analysis cannot establish whether reporting propensity increased within any individual category.

### Moderation response time

| Metric | Before Aug 15 | After Aug 15 |
|---|---:|---:|
| Mean of daily median action time | 7.9 hours | 11.9 hours |

The mean daily median action time increased by approximately 50.6%.

**Interpretation:** The simulated post-change period shows a meaningful slowdown in moderation response time. This could indicate increased operational pressure or a change in queue processing efficiency.

This is a before/after comparison on synthetic data, not proof that the policy change caused the slowdown.

### Analytical takeaway

Aggregate reporting metrics can conceal important changes in the composition of incoming reports.

Monitoring total report volume and exposure-normalised reporting rates should be complemented by category-level reporting mix analysis. Operational teams should monitor changes in category distribution alongside queue response times and workload.

---

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

Review a sample of overturned cases to identify recurring decision patterns before drawing conclusions about individual moderators.

---

## Finding 4 — Predictive risk modelling

A supervised machine-learning model was developed to identify users at risk of receiving an enforcement action within the next 14 days.

### Prediction question

"Today, for a user who has never been punished, will they receive an enforcement action in the next 14 days?"

The training dataset contains one row per eligible user per snapshot date.

Users with a prior enforcement action are excluded from the prediction population.

### Features

The model uses seven behavioural and account-level features:

- Account age in days.
- Number of linked accounts.
- Messages today.
- Messages in the previous 7 days.
- Reports today.
- Reports in the previous 7 days.
- Reports in the previous 30 days.

The model uses a HistGradientBoostingClassifier with monotonic constraints on the risk-related behavioural features.

### Temporal validation

A chronological split was used to reduce leakage and better reflect a production prediction setting.

| Dataset | Date range |
|---|---|
| Training | Through August 1, 2026 |
| Gap | August 2–15, 2026 |
| Validation | August 16–31, 2026 |
| Test | September 1–16, 2026 |

The gap separates training from validation, while validation and test evaluate the model after the simulated policy-change date.

### Model performance

| Metric | Model | Rules baseline |
|---|---:|---:|
| Validation PR-AUC | 0.184 | 0.079 |
| Validation ROC-AUC | 0.763 | 0.576 |
| Test PR-AUC | 0.118 | 0.065 |
| Test ROC-AUC | 0.698 | 0.571 |

The model outperformed the rules baseline on both PR-AUC and ROC-AUC in validation and test.

PR-AUC is particularly relevant because the positive enforcement outcome is relatively rare.

### Review capacity and performance

At a review capacity of 500 accounts per day:

| Metric | Model | Rules baseline |
|---|---:|---:|
| Precision@500 | 7.2% | 5.0% |
| Recall@500 | 22.7% | 15.6% |
| Lift@500 | 6.38x | 4.43x |
| Bad accounts caught per day | 35.9 | 24.9 |

The model identifies more future-enforced accounts than the rules baseline at the same review capacity.

This illustrates the importance of evaluating risk models at operational review capacity rather than relying exclusively on aggregate classification metrics.

### Feature importance

Permutation importance based on the decrease in PR-AUC:

| Feature | PR-AUC decrease |
|---|---:|
| Messages in previous 7 days | 0.0680 |
| Account age | 0.0541 |
| Reports in previous 30 days | 0.0097 |
| Reports today | 0.0053 |
| Reports in previous 7 days | 0.0032 |
| Messages today | 0.0017 |
| Linked accounts | 0.0003 |

Recent messaging activity and account age were the strongest predictive features in this experiment.

### Performance by planted archetype

Recall@500 by synthetic user archetype:

| Archetype | Model | Rules baseline |
|---|---:|---:|
| Normal | 0.079 | 0.099 |
| Repeat offender | 0.736 | 0.275 |
| Spam burst | 0.986 | 0.957 |

The model substantially improved recall for repeat offenders and spam-burst accounts.

However, it did not outperform the rules baseline for normal users. This reinforces the need to inspect model performance across different user populations rather than relying only on overall metrics.

### Interpretation and limitations

The model improves prioritisation over the rules baseline in this synthetic experiment, but its performance should not be interpreted as production-ready.

The dataset contains deliberately planted behavioural archetypes, and the temporal evaluation covers a limited simulation period.

The risk score should support human review prioritisation, not automatic enforcement.

---

## Planted patterns vs. recovered results

| Planted or simulated pattern | Pipeline result |
|---|---|
| Ring of 40 linked accounts | All 40 recovered; zero false positives in this dataset |
| Moderator with elevated overturn rate | Moderator 7: 9.40% vs. 2.31% pooled for other moderators |
| 1.5x slower moderation queue after the simulated change | Mean daily median action time increased from 7.9 to 11.9 hours (+50.6%) |
| Increased reporting after the simulated change | Aggregate reports per 1,000 messages remained broadly stable (-0.54%), while category composition shifted substantially |
| Future enforcement risk | Model test PR-AUC of 0.118 vs. 0.065 for the rules baseline |

The reporting-category result is intentionally presented as a composition shift rather than evidence of increased category-specific reporting propensity.

---

## Limitations

- The dataset is synthetic and contains deliberately planted patterns.
- Detection performance against planted ground truth does not establish real-world generalisation.
- Shared IPs and devices can create legitimate account relationships.
- Before/after comparisons do not establish causality.
- Message volume is used as the exposure denominator for aggregate reporting rates; other denominators may be appropriate for different product questions.
- Message-level policy categories are unavailable, preventing calculation of category-specific reporting rates.
- Report-category shares describe the composition of submitted reports, not the probability that a message in a particular category is reported.
- Moderator overturn rates should be interpreted alongside case mix, policy categories, and assignment patterns.
- The confidence interval reported for Moderator 7 is an approximate normal (Wald) interval.
- Risk-model results are based on synthetic data and should not be treated as production performance estimates.
- The risk model is designed for prioritisation and human review, not autonomous enforcement.
- Country-level review-flag comparisons cover only six countries and are diagnostic, not a fairness certification.

---

## Recommended next steps

### 1. Improve coordinated-abuse detection

Evaluate ring detection under different thresholds and more realistic patterns of shared devices and IP addresses.

Introduce additional independent behavioural signals and assess false-positive trade-offs.

### 2. Experiment with LLM-assisted report triage

Build an LLM-assisted triage prototype that classifies incoming reports, extracts relevant evidence, and recommends a policy category for human review.

Evaluate classification precision, recall, processing cost per 1,000 messages, reviewer agreement, and escalation accuracy against a rules baseline.

The model should assist human reviewers rather than make autonomous enforcement decisions.

### 3. Improve moderator quality monitoring

Add case-mix-adjusted moderator comparisons, category-level overturn rates, and minimum sample-size requirements.

### 4. Extend operational monitoring

Add rolling averages, anomaly detection, queue backlog, and SLA breach trends to identify emerging operational issues.

### 5. Improve risk-model evaluation

Evaluate additional temporal windows, review-capacity thresholds, and model calibration.

Monitor precision, recall, and false-positive rates across user populations before considering any production deployment.

---

## Tools and technologies

- SQL
- dbt Core
- DuckDB
- Python
- pandas
- scikit-learn
- matplotlib
- Synthetic data generation
- Data quality tests
- Git and GitHub
