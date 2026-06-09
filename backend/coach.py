# backend/coach.py
import os, pickle
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

model     = pickle.load(open("../models/xgb_model.pkl",      "rb"))
explainer = pickle.load(open("../models/shap_explainer.pkl",  "rb"))
client    = Groq(api_key=os.getenv("GROQ_API_KEY"))

FEATURES = [
    "stage_stall",
    "stage_instability",
    "competitor_flag",
    "qualification_speed",
    "base_win_rate",
    "deal_to_revenue_ratio"
]

def get_probability_and_shap(deal: dict):
    row       = pd.DataFrame([deal])[FEATURES].fillna(0)
    prob      = model.predict_proba(row)[0][1]
    shap_vals = explainer.shap_values(row)[0]
    shap_dict = {FEATURES[i]: round(float(shap_vals[i]), 3) for i in range(len(FEATURES))}
    top3      = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
    return round(prob * 100, 1), top3

def generate_recommendation(deal: dict, prob: float, top3: list, benchmarks: dict):
    drivers_str = "; ".join([f"{k.replace('_',' ')} impact={v:+.2f}" for k, v in top3])

    prompt = f"""You are a senior B2B sales manager reviewing a deal. Give specific, data-grounded advice.

DEAL DETAILS:
- Product Line: {deal.get('product_line')} | Product Group: {deal.get('product_group')}
- Region: {deal.get('region')} | Route To Market: {deal.get('route_to_market')}
- Deal Value (USD): ${deal.get('deal_value', 0):,.0f}
- Deal Size Category: {deal.get('deal_size_category')}
- Client Size (Revenue): {deal.get('client_size_revenue')}
- Client Revenue Past 2 Years: ${deal.get('client_revenue_2yr', 0):,.0f}
- Competitor Present: {'Yes — ' + str(deal.get('competitor_type')) if deal.get('competitor_flag') == 1 else 'No'}

DEAL PROGRESS:
- Days in Current Stage: {deal.get('days_in_stage')}
- Stage Changes So Far: {deal.get('stage_change_count')}
- Total Days Since Identified: {deal.get('total_days_closing')}

CLOSE PROBABILITY: {prob}%
TOP RISK DRIVERS (SHAP): {drivers_str}

SEGMENT BENCHMARKS:
- Win rate for {deal.get('product_line')}: {benchmarks.get('product_line_win_rate')}%
- Avg days to close for this product line: {benchmarks.get('product_line_avg_days')} days
- Win rate in {deal.get('region')}: {benchmarks.get('region_win_rate')}%
- Competitor presence rate in this region: {benchmarks.get('region_competitor_rate')}%

Respond in exactly this format:
SITUATION: [2 sentences describing where this deal stands]
WHAT THE DATA SAYS: [3 specific observations using the numbers above]
RECOMMENDED ACTION: [1 concrete next step with clear rationale]
WHAT TO AVOID: [1 specific mistake to avoid given this deal's profile]"""

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=450
        )
        return resp.choices[0].message.content
    except Exception as e:
        # Fallback if Groq fails
        drivers_str_fb = "; ".join([f"{k.replace('_',' ')} ({'+' if v>0 else ''}{v:.2f})" for k,v in top3])
        return f"""SITUATION: This deal has a {prob}% close probability in the {deal.get('product_line')} product line, {deal.get('region')} region.

WHAT THE DATA SAYS: Top risk drivers are {drivers_str_fb}. Benchmark win rate for this product line is {benchmarks.get('product_line_win_rate')}% and average days to close is {benchmarks.get('product_line_avg_days')} days. This deal has been in stage for {deal.get('days_in_stage')} days.

RECOMMENDED ACTION: {"Escalate immediately — deal probability is critically low. Re-engage decision maker directly." if prob < 35 else "Monitor closely and increase touch frequency." if prob < 65 else "Continue current approach — deal is on track."}

WHAT TO AVOID: {"Applying further discounts without movement." if deal.get('deal_to_revenue_ratio', 0) > 1 else "Reducing engagement frequency."}"""
