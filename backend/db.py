# backend/db.py
import os
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:postgres123@localhost:5432/postgres")

def get_all_deals():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM deals_features LIMIT 100")
        ).fetchall()
    return [dict(r._mapping) for r in rows]

def get_deal(deal_id: str):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM deals_features WHERE deal_id = :id"),
            {"id": deal_id}
        ).fetchone()
    return dict(row._mapping) if row else None

def get_benchmarks(product_line: str, region: str):
    with engine.connect() as conn:
        pl = conn.execute(
            text("SELECT * FROM segment_benchmarks WHERE segment_type='product_line' AND segment_value=:v"),
            {"v": product_line}
        ).fetchone()
        rg = conn.execute(
            text("SELECT * FROM segment_benchmarks WHERE segment_type='region' AND segment_value=:v"),
            {"v": region}
        ).fetchone()
    return {
        "product_line_win_rate":   round(pl._mapping["win_rate"]*100, 1) if pl else "N/A",
        "product_line_avg_days":   round(pl._mapping["avg_days_closing"], 1) if pl else "N/A",
        "region_win_rate":         round(rg._mapping["win_rate"]*100, 1) if rg else "N/A",
        "region_competitor_rate":  round(rg._mapping["competitor_rate"]*100, 1) if rg else "N/A",
    }
