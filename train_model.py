# train_model.py
import pandas as pd
import pickle
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
import xgboost as xgb
import shap

DB_URL = "postgresql://postgres:postgres123@localhost:5432/postgres"
engine = create_engine(DB_URL)
df     = pd.read_sql("SELECT * FROM deals_features", engine)

# These are the exact 6 features built in feature_engineering.py
FEATURES = [
    "stage_stall",
    "stage_instability",
    "competitor_flag",
    "qualification_speed",
    "base_win_rate",
    "deal_to_revenue_ratio"
]

X = df[FEATURES].fillna(0)
y = df["outcome_binary"]

# Stratified split keeps Won/Lost ratio same in train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    random_state=42,
    eval_metric="logloss"
)
model.fit(X_train, y_train)

# Evaluate — use AUC not accuracy
probs = model.predict_proba(X_test)[:, 1]
print(f"AUC Score: {roc_auc_score(y_test, probs):.3f}")
print(classification_report(y_test, model.predict(X_test)))

# Save trained model
pickle.dump(model,    open("models/xgb_model.pkl",     "wb"))

# Save SHAP explainer (used in backend/coach.py to explain each deal)
explainer = shap.TreeExplainer(model)
pickle.dump(explainer, open("models/shap_explainer.pkl", "wb"))
print("Saved: models/xgb_model.pkl and models/shap_explainer.pkl")
