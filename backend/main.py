# backend/main.py
import numpy as np
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy import text
import os

load_dotenv()

from db    import get_all_deals, get_deal, get_benchmarks, engine
from coach import get_probability_and_shap, generate_recommendation
from agents.sales_agent import run_agent
from services.scheduler import start_scheduler
from database.models import create_agent_tables

app = FastAPI(title="SalesSignal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Create agent tables and start scheduler on startup
@app.on_event("startup")
def startup_event():
    create_agent_tables()
    start_scheduler()

# ── Request models ──────────────────────────────────────
class ChatRequest(BaseModel):
    message:    str
    session_id: str = None

class ActionRequest(BaseModel):
    deal_id:     str
    action_type: str
    parameters:  dict = {}

# ── Helpers ─────────────────────────────────────────────
def clean(obj):
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean(v) for v in obj]
    elif isinstance(obj, (np.integer,)):   return int(obj)
    elif isinstance(obj, (np.floating,)):  return float(obj)
    elif isinstance(obj, (np.bool_,)):     return bool(obj)
    elif isinstance(obj, (np.ndarray,)):   return obj.tolist()
    return obj

# ── Existing endpoints ──────────────────────────────────
@app.get("/deals")
def list_deals():
    deals  = get_all_deals()
    result = []
    for d in deals:
        try:
            prob, _ = get_probability_and_shap(d)
            d["probability"] = round(float(prob), 1)
        except Exception:
            d["probability"] = 0.0
        result.append(clean(d))
    return result

@app.get("/deal/{deal_id}")
def deal_detail(deal_id: str):
    deal = get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    prob, top3 = get_probability_and_shap(deal)
    return clean({
        "deal":         deal,
        "probability":  round(float(prob), 1),
        "shap_drivers": [(k, round(float(v), 3)) for k, v in top3]
    })

@app.get("/risk/{deal_id}")
def risk_score(deal_id: str):
    deal = get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    prob, top3 = get_probability_and_shap(deal)
    risk = "HIGH" if prob < 35 else "MEDIUM" if prob < 65 else "LOW"
    return clean({
        "deal_id":     deal_id,
        "probability": round(float(prob), 1),
        "risk_level":  risk,
        "top_drivers": [(k, round(float(v), 3)) for k, v in top3]
    })

@app.post("/coach/{deal_id}")
def coach_deal(deal_id: str):
    deal = get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    prob, top3     = get_probability_and_shap(deal)
    benchmarks     = get_benchmarks(deal["product_line"], deal["region"])
    recommendation = generate_recommendation(deal, prob, top3, benchmarks)
    return clean({
        "deal_id":        deal_id,
        "probability":    round(float(prob), 1),
        "recommendation": recommendation
    })

@app.get("/benchmarks")
def benchmarks():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM segment_benchmarks")).fetchall()
    return clean([dict(r._mapping) for r in rows])

# ── NEW Agentic endpoints ────────────────────────────────
@app.post("/chat")
def chat(request: ChatRequest):
    """Main conversational agent endpoint."""
    session_id = request.session_id or str(uuid.uuid4())
    result     = run_agent(session_id, request.message)
    return result

@app.post("/agent/action")
def agent_action(request: ActionRequest):
    """Trigger a specific agent action on a deal."""
    message = f"For deal {request.deal_id}, perform action: {request.action_type} with parameters {request.parameters}"
    result  = run_agent(str(uuid.uuid4()), message)
    return result

@app.get("/agent/logs")
def agent_logs():
    """Get all logged agent actions."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM agent_actions ORDER BY created_at DESC LIMIT 50")
        ).fetchall()
    return clean([dict(r._mapping) for r in rows])

@app.get("/conversations/{session_id}")
def get_conversation(session_id: str):
    """Get conversation history for a session."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM conversations WHERE session_id=:sid ORDER BY created_at"),
            {"sid": session_id}
        ).fetchall()
    return [dict(r._mapping) for r in rows]
