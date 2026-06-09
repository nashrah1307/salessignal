# backend/services/scheduler.py
import pickle
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL    = os.getenv("DATABASE_URL")
engine    = create_engine(DB_URL)
model     = pickle.load(open("../models/xgb_model.pkl", "rb"))

FEATURES  = [
    "stage_stall", "stage_instability", "competitor_flag",
    "qualification_speed", "base_win_rate", "deal_to_revenue_ratio"
]

def check_stalled_deals():
    """
    Runs every 60 minutes.
    Finds deals that are high risk and logs them for agent review.
    """
    print("[Scheduler] Checking for stalled deals...")
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT * FROM deals_features LIMIT 200")
            ).fetchall()

        stalled = []
        for row in rows:
            d    = dict(row._mapping)
            X    = pd.DataFrame([d])[FEATURES].fillna(0)
            prob = model.predict_proba(X)[0][1] * 100
            if prob < 30 and (d.get("days_in_stage") or 0) > 14:
                stalled.append(d)

        print(f"[Scheduler] Found {len(stalled)} critically stalled deals")

        # Log each stalled deal to agent_actions
        with engine.connect() as conn:
            for d in stalled:
                conn.execute(
                    text("""
                        INSERT INTO agent_actions 
                            (deal_id, action_type, parameters, reason, priority, outcome)
                        VALUES 
                            (:deal_id, 'stall_detected', 
                             '{"auto_detected": true}'::jsonb,
                             'Deal stalled beyond threshold with low probability',
                             'high', 'pending_review')
                    """),
                    {"deal_id": str(d.get("deal_id", ""))}
                )
            conn.commit()

    except Exception as e:
        print(f"[Scheduler] Error: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_stalled_deals, "interval", minutes=60)
    scheduler.start()
    print("[Scheduler] Background deal monitor started")
    return scheduler
