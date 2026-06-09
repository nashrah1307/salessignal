# backend/tools/agent_tools.py
import pickle
import pandas as pd
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain.tools import tool
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URL  = os.getenv("DATABASE_URL")
engine  = create_engine(DB_URL)

model     = pickle.load(open("../models/xgb_model.pkl",     "rb"))
explainer = pickle.load(open("../models/shap_explainer.pkl", "rb"))

FEATURES = [
    "stage_stall", "stage_instability", "competitor_flag",
    "qualification_speed", "base_win_rate", "deal_to_revenue_ratio"
]

# ── TOOL 1 ──────────────────────────────────────────────
@tool
def get_deal_data(deal_id: str) -> str:
    """Get full deal information for a given deal_id."""
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT * FROM deals_features WHERE deal_id = :id"),
                {"id": deal_id}
            ).fetchone()
        if not row:
            return f"No deal found with ID {deal_id}"
        d = dict(row._mapping)
        return json.dumps({
            "deal_id":           d.get("deal_id"),
            "product_line":      d.get("product_line"),
            "region":            d.get("region"),
            "deal_value":        d.get("deal_value"),
            "days_in_stage":     d.get("days_in_stage"),
            "stage_changes":     d.get("stage_change_count"),
            "competitor":        d.get("competitor_type"),
            "deal_size":         d.get("deal_size_category"),
            "route_to_market":   d.get("route_to_market"),
            "client_revenue_2yr": d.get("client_revenue_2yr"),
        }, default=str)
    except Exception as e:
        return f"Error fetching deal: {str(e)}"
    
@tool
def get_all_segment_benchmarks() -> str:
    """Get win rates for all product lines, regions, deal sizes and routes to market. Use this to compare performance across segments."""
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT * FROM segment_benchmarks ORDER BY segment_type, win_rate ASC")
            ).fetchall()
        
        result = "Segment Benchmarks:\n\n"
        current_type = None
        for row in rows:
            d = dict(row._mapping)
            if d['segment_type'] != current_type:
                current_type = d['segment_type']
                result += f"\n{current_type.upper().replace('_',' ')}:\n"
            result += f"  {d['segment_value']}: win rate={round(d['win_rate']*100,1)}%, avg days to close={round(d['avg_days_closing'],1)}\n"
        return result
    except Exception as e:
        return f"Error fetching benchmarks: {str(e)}"

# ── TOOL 2 ──────────────────────────────────────────────
@tool
def get_risk_score(deal_id: str) -> str:
    """Get the close probability risk score for a deal."""
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT * FROM deals_features WHERE deal_id = :id"),
                {"id": deal_id}
            ).fetchone()
        if not row:
            return f"Deal {deal_id} not found"
        d    = dict(row._mapping)
        X    = pd.DataFrame([d])[FEATURES].fillna(0)
        prob = model.predict_proba(X)[0][1]
        risk = "HIGH RISK" if prob < 0.35 else "MEDIUM RISK" if prob < 0.65 else "LOW RISK"
        return f"Deal {deal_id} close probability: {round(prob*100,1)}% — {risk}"
    except Exception as e:
        return f"Error calculating risk: {str(e)}"

# ── TOOL 3 ──────────────────────────────────────────────
@tool
def get_shap_explanation(deal_id: str) -> str:
    """Get SHAP explanation showing which factors are driving deal risk."""
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT * FROM deals_features WHERE deal_id = :id"),
                {"id": deal_id}
            ).fetchone()
        if not row:
            return f"Deal {deal_id} not found"
        d         = dict(row._mapping)
        X         = pd.DataFrame([d])[FEATURES].fillna(0)
        shap_vals = explainer.shap_values(X)[0]
        shap_dict = {FEATURES[i]: round(float(shap_vals[i]), 3) for i in range(len(FEATURES))}
        top3      = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        result    = "Top risk drivers:\n"
        for feat, val in top3:
            direction = "HURTING" if val < 0 else "HELPING"
            result   += f"  - {feat.replace('_',' ')}: {val:+.3f} ({direction})\n"
        return result
    except Exception as e:
        return f"Error generating SHAP explanation: {str(e)}"

# ── TOOL 4 ──────────────────────────────────────────────
@tool
def get_segment_benchmarks(product_line: str, region: str) -> str:
    """Get benchmark win rates and average days to close for a product line and region."""
    try:
        with engine.connect() as conn:
            pl = conn.execute(
                text("SELECT * FROM segment_benchmarks WHERE segment_type='product_line' AND segment_value=:v"),
                {"v": product_line}
            ).fetchone()
            rg = conn.execute(
                text("SELECT * FROM segment_benchmarks WHERE segment_type='region' AND segment_value=:v"),
                {"v": region}
            ).fetchone()
        result = f"Benchmarks for {product_line} in {region}:\n"
        if pl:
            result += f"  Product line win rate: {round(pl._mapping['win_rate']*100,1)}%\n"
            result += f"  Avg days to close: {round(pl._mapping['avg_days_closing'],1)}\n"
        if rg:
            result += f"  Region win rate: {round(rg._mapping['win_rate']*100,1)}%\n"
            result += f"  Competitor presence rate: {round(rg._mapping['competitor_rate']*100,1)}%\n"
        return result
    except Exception as e:
        return f"Error fetching benchmarks: {str(e)}"

# ── TOOL 5 ──────────────────────────────────────────────

@tool
def get_at_risk_deals(threshold: float) -> str:
    """Get all deals below a given probability threshold. Use 35.0 as default. Scores deals in batch for speed."""
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT * FROM deals_features LIMIT 200")
            ).fetchall()
        
        deals = [dict(row._mapping) for row in rows]
        df_all = pd.DataFrame(deals)[FEATURES].fillna(0)
        
        # Score all deals in one batch call — much faster
        probs = model.predict_proba(df_all)[:, 1] * 100
        
        at_risk = []
        for i, d in enumerate(deals):
            if probs[i] < threshold:
                at_risk.append({
                    "deal_id":      d.get("deal_id"),
                    "product_line": d.get("product_line"),
                    "region":       d.get("region"),
                    "deal_value":   d.get("deal_value"),
                    "probability":  round(float(probs[i]), 1)
                })
        
        at_risk.sort(key=lambda x: x["probability"])
        result = f"Found {len(at_risk)} at-risk deals (below {threshold}%):\n"
        for d in at_risk[:10]:
            result += f"  Deal {d['deal_id']}: {d['probability']}% — {d['product_line']} / {d['region']} — ${d['deal_value']:,.0f}\n"
        return result
    except Exception as e:
        return f"Error: {str(e)}"
    
# ── TOOL 6 ──────────────────────────────────────────────
@tool
def send_email(to_email: str, subject: str, body: str) -> str:
    """Send an email to a client or team member."""
    try:
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_pass = os.getenv("SMTP_PASSWORD", "")

        if not smtp_user or smtp_user == "your@gmail.com":
            # Mock mode — log instead of actually sending
            log_action("email_sent", {"to": to_email, "subject": subject, "body": body}, "Mock email logged")
            return f"[MOCK] Email logged to {to_email} with subject: {subject}"

        msg            = MIMEMultipart()
        msg["From"]    = smtp_user
        msg["To"]      = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())

        log_action("email_sent", {"to": to_email, "subject": subject}, "Email sent successfully")
        return f"Email sent successfully to {to_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"

# ── TOOL 7 ──────────────────────────────────────────────
@tool
def update_crm(deal_id: str, status: str, notes: str = "") -> str:
    """Update the CRM status of a deal in the database."""
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO deal_state_history (deal_id, previous_probability, new_probability)
                    SELECT :deal_id,
                           (SELECT AVG(new_probability) FROM deal_state_history WHERE deal_id=:deal_id),
                           NULL
                """),
                {"deal_id": deal_id}
            )
            conn.commit()
        log_action("crm_update", {"deal_id": deal_id, "status": status, "notes": notes}, "CRM updated")
        return f"CRM updated for deal {deal_id} — status set to: {status}"
    except Exception as e:
        return f"Error updating CRM: {str(e)}"

# ── TOOL 8 ──────────────────────────────────────────────
@tool
def schedule_meeting(deal_id: str, contact_name: str, proposed_time: str) -> str:
    """Schedule a meeting for a deal. Logs the scheduling action."""
    try:
        log_action("meeting_scheduled", {
            "deal_id":       deal_id,
            "contact":       contact_name,
            "proposed_time": proposed_time
        }, "Meeting scheduled")
        return f"Meeting scheduled with {contact_name} for deal {deal_id} at {proposed_time}"
    except Exception as e:
        return f"Error scheduling meeting: {str(e)}"

# ── Helper ───────────────────────────────────────────────
def log_action(action_type: str, parameters: dict, outcome: str):
    """Log every agent action to the database."""
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO agent_actions (action_type, parameters, outcome)
                    VALUES (:action_type, :parameters::jsonb, :outcome)
                """),
                {
                    "action_type": action_type,
                    "parameters":  json.dumps(parameters),
                    "outcome":     outcome
                }
            )
            conn.commit()
    except Exception:
        pass
    
@tool
def get_highest_risk_deals() -> str:
    """Get the top 10 highest risk deals with the lowest close probability."""
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT * FROM deals_features LIMIT 200")
            ).fetchall()
        
        deals = [dict(row._mapping) for row in rows]
        df_all = pd.DataFrame(deals)[FEATURES].fillna(0)
        probs  = model.predict_proba(df_all)[:, 1] * 100
        
        scored = [{
            "deal_id":       d.get("deal_id"),
            "product_line":  d.get("product_line"),
            "region":        d.get("region"),
            "deal_value":    d.get("deal_value"),
            "days_in_stage": d.get("days_in_stage"),
            "probability":   round(float(probs[i]), 1)
        } for i, d in enumerate(deals)]
        
        scored.sort(key=lambda x: x["probability"])
        result = "Top 10 highest risk deals:\n"
        for d in scored[:10]:
            result += f"  Deal {d['deal_id']}: {d['probability']}% — {d['product_line']} / {d['region']} — ${d['deal_value']:,.0f} — {d['days_in_stage']} days in stage\n"
        return result
    except Exception as e:
        return f"Error: {str(e)}"
