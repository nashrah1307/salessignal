# backend/db/models.py
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL)

def create_agent_tables():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agent_actions (
                id SERIAL PRIMARY KEY,
                deal_id VARCHAR,
                action_type VARCHAR,
                parameters JSONB,
                reason TEXT,
                priority VARCHAR,
                outcome TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR,
                role VARCHAR,
                message TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS deal_state_history (
                id SERIAL PRIMARY KEY,
                deal_id VARCHAR,
                previous_probability FLOAT,
                new_probability FLOAT,
                changed_at TIMESTAMP DEFAULT NOW()
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS action_logs (
                id SERIAL PRIMARY KEY,
                action_id INT REFERENCES agent_actions(id),
                log_message TEXT,
                logged_at TIMESTAMP DEFAULT NOW()
            );
        """))
        conn.commit()
        print("Agent tables created successfully")

if __name__ == "__main__":
    create_agent_tables()
