import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql://postgres:postgres123@localhost:5432/postgres"
engine  = create_engine(DB_URL)
df      = pd.read_sql("SELECT * FROM deals", engine)

# FEATURE 1: Stage stall
# How many more days is this deal in its stage vs the median won deal?
# Uses: days_in_stage
median_won_days = df[df.outcome == "Won"]["days_in_stage"].median()
df["stage_stall"] = df["days_in_stage"] - median_won_days

# FEATURE 2: Stage instability
# Deals that keep changing stages are losing direction
# Uses: stage_change_count
df["stage_instability"] = df["stage_change_count"].fillna(0)

# FEATURE 3: Competitor present flag
# 1 if any competitor is listed, 0 if empty/None/nan
# Uses: competitor_type
df["competitor_flag"] = (
    df["competitor_type"].notna() &
    (~df["competitor_type"].str.strip().str.lower().isin(["none", "no competitor", ""]))
).astype(int)

# FEATURE 4: Qualification speed ratio
# Higher = deal moved through qualification faster = good signal
# Uses: ratio_qualified (already a ratio column in your data)
df["qualification_speed"] = df["ratio_qualified"].fillna(0)

# FEATURE 5: Historical win rate for this product line + region
# Uses: product_line, region, outcome_binary
base_wr = df.groupby(["product_line", "region"])["outcome_binary"].transform("mean")
df["base_win_rate"] = base_wr.round(3)

# FEATURE 6: Deal size relative to client past revenue
# Big deal from small client = risky
# Uses: deal_value, client_revenue_2yr
df["deal_to_revenue_ratio"] = (
    df["deal_value"] / (df["client_revenue_2yr"] + 1)
).fillna(0)

print("Features created:")
print(df[["deal_id","stage_stall","stage_instability","competitor_flag",
          "qualification_speed","base_win_rate","deal_to_revenue_ratio"]].head())

df.to_sql("deals_features", engine, if_exists="replace", index=False)
print(f"Saved {len(df)} rows to deals_features table")
