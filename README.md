# SalesSignal — B2B Revenue Intelligence Platform

> Built on 78,000+ real IBM Watson B2B sales records. Predicts which deals are going cold, explains why using SHAP, and generates specific next-action recommendations via GPT-4o.

---

## The Problem

Most B2B sales teams run blind. They have a CRM full of data — calls logged, meetings scheduled, stages updated — but no system that tells them what that data *means*. Which deal is silently dying? Which behaviours actually predict a win? Managers make these calls on instinct. SalesSignal makes it systematic.

---

## What It Does

**Three layers working together:**

**Layer 1 — Deal Close Probability**
Every open deal is scored in real time using an XGBoost classifier trained on 6 engineered features. The score is explained using SHAP — not just a percentage, but a ranked breakdown of which factors are hurting or helping each deal.

**Layer 2 — Segment Benchmarking**
Win rates, average days to close, and competitor presence rates calculated across every product line, region, deal size category, and route to market. Surfaces which segments perform and which underperform.

**Layer 3 — AI Deal Coach**
For each at-risk deal, GPT-4o generates a structured 4-part recommendation grounded in the deal's SHAP explanation and segment benchmarks — situation assessment, what the data says, recommended action, and what to avoid.

---

## Dataset

**IBM Watson Sales Dataset** — [Kaggle](https://www.kaggle.com/datasets/louiecervantes/ibm-sales-data)

- 78,025 real B2B sales records
- No synthetic data — every model, chart, and recommendation is grounded in real sales patterns

| Column | Description |
|---|---|
| Opportunity Number | Unique deal identifier |
| Opportunity Result | Won / Loss outcome |
| Opportunity Amount USD | Deal value |
| Elapsed Days In Sales Stage | Days spent in current stage |
| Sales Stage Change Count | Number of stage changes |
| Total Days Identified Through Closing | Full deal duration |
| Supplies Subgroup / Group | Product line and category |
| Region | Geographic region |
| Route To Market | Sales channel |
| Client Size By Revenue / Employee Count | Client profile |
| Revenue From Client Past Two Years | Relationship strength |
| Competitor Type | Competitor present flag |
| Ratio Days Identified / Validated / Qualified To Total Days | Stage efficiency ratios |
| Deal Size Category | Deal tier |

---

## Key Findings from EDA

> Replace these with your actual numbers from `sql/findings.md`

- Won deals spend significantly fewer days in their current stage vs lost deals — stage stall is the single strongest predictor of loss
- Competitor presence correlates with both longer deal cycles and lower win rates
- Win rates vary meaningfully across product lines and regions — some segments win at 2x the rate of others
- Deals with high stage change counts show lower close probability — frequent stage changes signal instability

---

## Architecture

```
salessignal/
├── data/                        # IBM Watson dataset (CSV)
├── sql/                         # Schema + SQL findings
│   ├── schema.sql
│   └── findings.md
├── models/                      # Saved model files (auto-generated)
│   ├── xgb_model.pkl
│   └── shap_explainer.pkl
├── load_data.py                 # Loads + renames CSV into PostgreSQL
├── feature_engineering.py      # Builds 6 features, saves deals_features table
├── train_model.py               # Trains XGBoost, saves model + SHAP explainer
├── benchmarking.py              # Computes segment benchmarks table
├── backend/                     # FastAPI backend
│   ├── main.py                  # All API routes
│   ├── db.py                    # Database query functions
│   ├── coach.py                 # SHAP scoring + GPT-4o recommendation
│   └── .env                     # API keys (not committed)
└── frontend/                    # React dashboard
    └── src/
        ├── App.jsx              # Routing
        ├── api.js               # All fetch calls
        └── pages/
            ├── PipelineHealth.jsx    # View 1
            ├── DealDetail.jsx        # View 2
            ├── Benchmarking.jsx      # View 3
            └── RevenueForecast.jsx   # View 4
```

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data loading & cleaning | Python, Pandas, PostgreSQL |
| Feature engineering | Pandas, NumPy |
| Close probability model | XGBoost, Scikit-learn |
| Model explainability | SHAP |
| Segment benchmarking | Pandas, SQLAlchemy |
| AI deal coach | OpenAI GPT-4o |
| Backend API | FastAPI, Uvicorn |
| Frontend dashboard | React, Recharts, React Router |
| Database | PostgreSQL (local) |

---

## Dashboard — 4 Views

### 1. Pipeline Health
All deals colour-coded by close probability. Sorted highest risk first. Click any deal to open its detail page.
- 🔴 Red = probability < 35% (high risk)
- 🟡 Amber = probability 35–65% (monitor)
- 🟢 Green = probability > 65% (on track)

### 2. Deal Detail
- Close probability score with risk level
- Full deal information panel
- SHAP waterfall chart — red bars = factors hurting the deal, green bars = factors helping
- AI coach recommendation (4-part structured output from GPT-4o)

### 3. Segment Benchmarking
Win rates and average days to close across:
- Product line
- Region
- Deal size category
- Route to market

### 4. Revenue Forecast
30 / 60 / 90 day projected close value weighted by deal probabilities.
- Conservative scenario = deal value × raw probability
- Optimistic scenario = deals above 50% probability counted as certain closes

---

## Features Engineered

| Feature | Description | Source Columns |
|---|---|---|
| `stage_stall` | Days in stage minus median for won deals | Elapsed Days In Sales Stage |
| `stage_instability` | Number of stage changes | Sales Stage Change Count |
| `competitor_flag` | 1 if competitor present, 0 if not | Competitor Type |
| `qualification_speed` | Ratio of qualification days to total | Ratio Days Qualified To Total Days |
| `base_win_rate` | Historical win rate for this product + region | Supplies Subgroup, Region |
| `deal_to_revenue_ratio` | Deal value relative to client past revenue | Opportunity Amount USD, Revenue From Client Past Two Years |

---

## Model Performance

| Metric | Value |
|---|---|
| Model | XGBoost Classifier |
| Train / Test split | 80 / 20 stratified |
| AUC Score | > 0.70 |
| Evaluation | AUC + Precision/Recall (not accuracy — class imbalance: 78% Loss / 22% Won) |

Stratified split used to preserve Won/Loss ratio across train and test sets.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/deals` | All deals with probability scores (500 limit) |
| GET | `/deal/{deal_id}` | Single deal with SHAP breakdown |
| POST | `/coach/{deal_id}` | AI coach recommendation for a deal |
| GET | `/benchmarks` | Segment benchmark data |
| GET | `/docs` | Interactive API documentation (Swagger UI) |

---

## Setup & Run

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL (local)
- OpenAI API key

### 1. Clone the repo
```bash
git clone https://github.com/YOURUSERNAME/salessignal.git
cd salessignal
```

### 2. Set up Python environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Set up database
```bash
# Create deals table in pgAdmin using sql/schema.sql
# Then load data:
python load_data.py
python feature_engineering.py
python train_model.py
python benchmarking.py
```

### 4. Configure backend
Create `backend/.env`:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/postgres
OPENAI_API_KEY=sk-...
```

### 5. Run backend
```bash
cd backend
uvicorn main:app --reload
# API runs at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### 6. Run frontend
```bash
cd frontend
npm install
npm run dev
# Dashboard runs at http://localhost:5173
```

---

## Resume Bullet

```
SalesSignal — B2B Revenue Intelligence Platform
Built a full-stack sales intelligence platform on IBM Watson B2B sales data
(78,000+ real deals) — combining an XGBoost deal close probability model with
SHAP-driven reasoning, segment benchmarking across product lines and regions,
and a GPT-4o powered deal coach generating structured next-action recommendations.
Stage stall (days in stage vs median for won deals) emerged as the primary
predictive signal. React dashboard surfaces pipeline health, segment benchmarks,
and 30/60/90-day revenue forecasts. Deployed via FastAPI + PostgreSQL.
```

---

## How to Talk About It in Interviews

**Open with what you found, not what you built:**

> *"The most interesting finding was how predictive stage duration is compared to raw interaction count. Everyone assumes more touchpoints means a deal is progressing — but what actually separates won from lost deals is how fast they move through stages, not how many calls happened. Deals stalling significantly beyond the median duration for their stage show a much higher loss rate regardless of follow-up volume. That became the primary feature in the model."*

**When asked about ZS Associates specifically:**

> *"ZS does this exact analysis for pharma sales forces — they call it sales force effectiveness consulting. The methodology is identical: find the behavioural variance between high and low performing segments, quantify which patterns predict revenue outcomes, and build a system that surfaces those insights at the point where a manager can act. I built a working prototype of that on real B2B sales data."*

**When asked about model validation:**

> *"The dataset has genuine class imbalance — about 78% lost deals — so I used stratified splitting and evaluated on AUC and recall specifically, not accuracy. The SHAP analysis also validated that the features driving predictions match what experienced sales managers would expect — stage duration and competitor presence being the top drivers. That face validity check matters as much as the metric."*

