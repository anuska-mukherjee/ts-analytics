![dbt CI](https://github.com/anuska-mukherjee/ts-analytics/actions/workflows/ci.yml/badge.svg)

# Trust & Safety Analytics: Abuse Detection, Moderation Quality & Predictive Risk Intelligence

An end-to-end analytics engineering and machine learning project exploring coordinated account abuse, moderation quality, enforcement outcomes, predictive risk scoring, and platform safety operations using SQL, dbt, DuckDB, and Python.

## Executive Summary

This project builds a modular Trust & Safety analytics pipeline that transforms raw platform activity into actionable operational intelligence.

Using a synthetic dataset of 20,000 users, the pipeline identifies coordinated account networks, evaluates moderator enforcement quality, monitors moderation performance, and predicts the likelihood of future enforcement actions.

**Key findings:**

- Identified all 40 deliberately planted coordinated-ring accounts, with no false positives in the synthetic validation dataset.
- Identified a moderator with a 9.40% appeal overturn rate, compared with 2.31% across other moderators pooled.
- Detected a 50.6% increase in mean daily median moderation action time after the simulated policy-change date.
- Identified a sharp shift in report composition after the simulated August 15 policy change: harassment increased from 17.84% to 53.82% of reports (+35.97 percentage points), while spam declined from 67.11% to 39.09%.
- Developed a predictive risk model achieving a test PR-AUC of 0.118, compared with 0.065 for a rules-based baseline.
- Achieved 22.7% recall at a review capacity of 500 accounts per day, with approximately 6.38x lift over random review.

> This project uses synthetic data and simulated patterns. Results demonstrate analytical methodology, not production detection performance.

## Business Problems

Trust & Safety teams face several interconnected challenges:

1. **Coordinated abuse:** How can potentially related accounts be identified through shared devices, signup IPs, and behavioural signals?
2. **Moderation quality:** Are enforcement decisions consistent, and do appeal overturns reveal potential quality issues?
3. **Operational efficiency:** Are reports being actioned within SLA, and are moderation queues becoming slower?
4. **Platform health:** Are changes in report volume accompanied by changes in the composition of reported behaviour?
5. **Proactive risk detection:** Can accounts likely to receive enforcement actions be prioritised for investigation before an enforcement event occurs?

## Data Architecture

The project follows a layered dbt architecture:

| Layer | Purpose |
|---|---|
| Raw sources | Synthetic platform, user, device, report, moderation and appeal data |
| Staging | Standardisation, type casting, and sensitive identifier hashing |
| Intermediate | Account linking, report history, and report-to-action transformations |
| Marts | Analytical facts, dimensions, moderator quality, operational KPIs and user risk snapshots |
| ML pipeline | Training data generation, predictive modelling, evaluation and latest-user scoring |

### Technology Stack

- **SQL:** Analytical transformations and feature engineering
- **dbt Core:** Data modelling, testing, documentation and lineage
- **DuckDB:** Local analytical database
- **Python:** Synthetic data generation, model training and evaluation
- **Pandas:** Data preparation and analysis
- **Scikit-learn:** Predictive modelling and evaluation
- **GitHub Actions:** Automated CI checks

## Key Findings

### 1. Coordinated Account Abuse Detection

The project simulates coordinated account networks using shared device identifiers and signup IP addresses.

The account-linking pipeline builds relationships between users and aggregates network-level signals to identify suspicious clusters.

**Results:**

| Metric | Result |
|---|---:|
| Total synthetic users | 20,000 |
| Planted coordinated-ring accounts | 40 |
| True positives | 40 |
| False positives | 0 |
| False negatives | 0 |
| Precision | 100% |
| Recall | 100% |

The planted ring shared six devices and five signup IP addresses.


#### Detection threshold sensitivity

| Minimum linked accounts | Precision | Recall |
|---:|---:|---:|
| 1 | 4.98% | 100% |
| 2 | 59.70% | 100% |
| 3 | 100% | 100% |
| 5 | 100% | 100% |
| 10 | 100% | 87.50% |

A threshold of three linked accounts identified all 40 planted ring accounts without false positives. Raising the threshold to five preserved performance, while a threshold of ten missed five accounts.


**Business implication:** Shared infrastructure signals can help investigators identify potentially coordinated networks. In a production environment, these signals would require time-aware analysis, confidence thresholds, and contextual investigation before enforcement.

### 2. Reporting Patterns and Policy-Period Changes

The project compares platform reporting patterns before and after the simulated policy change on August 15, 2026.

The analysis examines report volume, platform activity, category composition, and moderation response times.

#### Overall reporting and activity

| Metric | Before | After |
|---|---:|---:|
| Average daily reports | 91 | 213 |
| Average daily messages | 51,529 | 124,603 |
| Reports per 1,000 messages | 80.36 | 79.93 |
| Mean daily median action time | 7.9 hours | 11.9 hours |

Reports per 1,000 messages declined by approximately 0.54%, while mean daily median moderation action time increased by approximately 50.6%.

#### Report-category mix shift

The composition of reports changed substantially after August 15.

| Report category | Before reports | After reports | Before share | After share | Change |
|---|---:|---:|---:|---:|---:|
| Harassment | 732 | 5,381 | 17.84% | 53.82% | +35.97 pp |
| Spam | 2,753 | 3,909 | 67.11% | 39.09% | -28.02 pp |
| Scam | 617 | 709 | 15.04% | 7.09% | -7.95 pp |

Harassment became the largest report category, increasing from 17.84% to 53.82% of all reports.

**Business implication:** Monitoring total report volume alone can conceal meaningful changes in the types of abuse reaching moderation teams. Operational teams should monitor category composition alongside queue response times, workload, and exposure-normalised reporting metrics.

**Interpretation caveat:** This is a before-and-after comparison using synthetic data. It does not establish that the policy change caused the observed shift. The available dataset also does not provide category-level message exposure, so category-specific reporting propensity cannot be calculated.

### 3. Moderator Quality and Appeal Outcomes

The project evaluates moderation outcomes using appeal overturn rates as a quality signal.

One moderator showed a substantially higher overturn rate than the pooled rate for other moderators.

| Metric | Moderator 7 | Other moderators |
|---|---:|---:|
| Enforcement actions | 1,390 | 9,684 |
| Overturned appeals | 130 | 224 |
| Overturn rate | 9.40% | 2.31% |

The moderator's overturn rate was approximately 4.1 times the pooled rate for other moderators, a difference of approximately 7.09 percentage points.

A rough Wald 95% confidence interval for Moderator 7's overturn rate is 7.87%–10.93%.

**Business implication:** Appeal overturn rates can help identify cases or workflows requiring further quality review. However, a higher overturn rate alone does not establish poor moderator performance.

Case complexity, policy category, enforcement severity, assignment patterns, and reviewer experience should be considered before drawing conclusions.

### 4. Predictive User Risk Modelling

The project extends descriptive analytics into predictive modelling by estimating the likelihood that an account will receive an enforcement action within the next 14 days.

**Prediction question:**

> For a user who has never been punished, will they receive an enforcement action in the next 14 days?

#### Model design

- One observation per eligible user per day.
- Only users with no previous enforcement action are included.
- Target variable: `enforced_next_14d`.
- Seven behavioural and account-level features.
- Temporal train, validation, and test separation.
- A 14-day gap between training and validation periods to reduce target-window overlap.

**Features:**

- Account age
- Linked accounts
- Messages today
- Messages over the previous 7 days
- Reports today
- Reports over the previous 7 days
- Reports over the previous 30 days

#### Temporal evaluation

| Dataset | Snapshot dates | Purpose |
|---|---|---|
| Training | Through August 1, 2026 | Model fitting |
| Gap | August 2–15, 2026 | Separation between training and validation |
| Validation | August 16–31, 2026 | Model selection |
| Test | September 1–16, 2026 | Final evaluation |

Validation and test periods occur after the simulated policy-change date, while training data precedes it.

#### Model performance

| Metric | Predictive model | Rules baseline |
|---|---:|---:|
| Validation PR-AUC | 0.184 | 0.079 |
| Test PR-AUC | 0.118 | 0.065 |
| Test ROC-AUC | 0.698 | 0.571 |
| Recall at K = 500 | 22.7% | 15.6% |
| Precision at K = 500 | 7.2% | 5.0% |
| Lift at K = 500 | 6.38x | 4.43x |

The predictive model outperformed the rules-based baseline on the reported test metrics.

#### Review-capacity trade-off

The model ranks eligible accounts by predicted risk. The top K accounts are selected for review, allowing the team to evaluate performance at different operational capacities.

At a review capacity of 500 accounts per day:

- Approximately 22.7% of accounts that would receive enforcement within the prediction window were captured.
- Precision was approximately 7.2%.
- The model achieved approximately 6.38x lift over random review.
- Approximately 35.9 accounts receiving enforcement within the prediction window were identified per day.

The model also evaluates estimated review costs and missed-account costs at multiple daily review capacities.

#### Model explainability

Permutation importance on the validation set showed the following approximate PR-AUC decreases when each feature was shuffled:

| Feature | PR-AUC decrease |
|---|---:|
| Messages over 7 days | 0.0680 |
| Account age | 0.0541 |
| Reports over 30 days | 0.0097 |
| Reports today | 0.0053 |
| Reports over 7 days | 0.0032 |
| Messages today | 0.0017 |
| Linked accounts | 0.0003 |

Recent messaging activity and account age were the strongest contributors to model performance in this experiment.

#### Performance by synthetic account archetype

| Account archetype | Model recall@500 | Rules recall@500 |
|---|---:|---:|
| Normal | 7.9% | 9.9% |
| Repeat offender | 73.6% | 27.5% |
| Spam burst | 98.6% | 95.7% |

The model performed particularly well on the planted repeat-offender and spam-burst patterns, while the rules baseline performed slightly better for normal accounts.

These results reflect the synthetic dataset's planted behaviour and should not be interpreted as expected production performance.

#### Latest-user scoring

The scoring pipeline generates a prioritised queue from the latest available user-risk snapshot.

- Eligible users scored: 17,890
- Review queue size: 500
- Latest snapshot date: September 30, 2026
- Output table: `ml_risk_scores`

The scores are intended to support investigation prioritisation, not automated enforcement.

## Engineering Practices

The project incorporates several analytics engineering practices:

- **Layered dbt architecture:** Separates raw-source transformations, intermediate logic, and analytical marts.
- **Incremental modelling:** Uses incremental processing for user-risk daily snapshots.
- **Snapshots:** Tracks user-status changes over time through dbt snapshots.
- **Reusable macros:** Centralises reusable SQL logic.
- **Data quality testing:** Uses uniqueness, not-null, relationship, and custom assertion tests.
- **dbt-utils:** Uses reusable data tests, including composite-key uniqueness checks.
- **Sensitive data handling:** Hashes email addresses and signup IP identifiers in staging models before downstream analysis.
- **Temporal leakage audit:** Reviewed account-link features and corrected the risk mart to calculate linked accounts as of each snapshot date.
- **Version control and CI:** Uses GitHub pull requests and automated dbt checks.

The project currently contains 55 dbt data tests, one snapshot, and seven declared sources.

## Repository Structure

```text
ts-analytics/
│
├── data/
│   ├── raw/
│   └── answer_key/
│
├── data_gen/
│   ├── gen_users.py
│   └── gen_activity.py
│
├── analysis/
│   ├── findings.md
│   ├── check_policy_stratified.py
│   └── risk_model/
│       ├── train.py
│       ├── explain.py
│       └── score_latest.py
│
├── dbt_project/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── macros/
│   ├── seeds/
│   ├── snapshots/
│   ├── tests/
│   ├── dbt_project.yml
│   └── profiles.yml
│
├── docs/
│   └── lineage.png
│
├── .github/
│   └── workflows/
│
├── requirements.txt
└── README.md
```

Synthetic raw data, answer keys, local database files, and trained model artifacts are excluded from version control.

## Setup and Reproduction

### Requirements

- Python 3.12
- Git
- dbt Core
- DuckDB
- Windows, macOS, or Linux

### 1. Clone the repository

```bash
git clone https://github.com/anuska-mukherjee/ts-analytics.git
cd ts-analytics
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate synthetic data

Run the data generators from the project root:

```bash
python data_gen/gen_users.py
python data_gen/gen_activity.py
```

### 5. Build the dbt project

From the project root:

```bash
cd dbt_project
```

Set the local dbt profile directory:

**Windows PowerShell:**

```powershell
$env:DBT_PROFILES_DIR = "$PWD"
```

**macOS / Linux:**

```bash
export DBT_PROFILES_DIR="$PWD"
```

Check the connection:

```bash
dbt debug
```

Run the models and tests:

```bash
dbt build
```

Generate dbt documentation:

```bash
dbt docs generate
```

### 6. Train and evaluate the risk model

From the project root:

```bash
python analysis/risk_model/train.py
python analysis/risk_model/explain.py
python analysis/risk_model/score_latest.py
```

The risk model scripts produce local evaluation outputs and update the DuckDB database.

## Limitations and Considerations

- The dataset is synthetic, and several abuse patterns were deliberately planted to validate detection logic.
- The coordinated-ring results reflect a controlled validation dataset and do not demonstrate real-world detection accuracy.
- Report volumes and category distributions are simulated; their base rates may not reflect realistic platform reporting behaviour.
- Before-and-after comparisons do not establish causality.
- Overall reports per 1,000 messages do not replace category-level exposure-normalised rates. Category-specific message exposure is not available in the current dataset.
- Moderator overturn rates require case-mix adjustment and contextual review.
- Predictive model performance is sensitive to synthetic labels, planted archetypes, and the simulated policy change.
- The risk model is a prioritisation experiment, not an automated enforcement system.
- Review-capacity and missed-account costs are illustrative assumptions rather than measured production costs.
- The country-level diagnostic covers only six synthetic countries and is not a fairness certification.

## Future Improvements

1. **Coordinated abuse detection:** Extend account-link analysis with behavioural similarity, time-aware graph features, and network investigation tools.
2. **LLM-assisted triage:** Evaluate policy-based message classification against a manually labelled sample and a rules-based baseline.
3. **Moderator quality:** Add case-mix-adjusted comparisons, category-level overturn rates, and minimum sample-size requirements.
4. **Operational monitoring:** Build an interactive dashboard for moderation operations, quality, and predictive risk.
5. **Predictive modelling:** Test additional temporal features, calibration, threshold robustness, and drift monitoring.
6. **Production readiness:** Add model monitoring, reproducible scoring, and deployment safeguards.


**Project focus:** Trust & Safety Analytics · Abuse Detection · Predictive Risk Modelling · Moderation Operations · Analytics Engineering · Product Analytics

[GitHub Repository](https://github.com/anuska-mukherjee/ts-analytics)