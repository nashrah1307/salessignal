import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql://postgres:postgres123@localhost:5432/postgres"
engine = create_engine(DB_URL)
df     = pd.read_sql("SELECT * FROM deals_features", engine)

# Benchmark 1: By product_line
by_product = df.groupby("product_line").agg(
    total_deals       = ("outcome_binary", "count"),
    win_rate          = ("outcome_binary", "mean"),
    avg_days_closing  = ("total_days_closing", "mean"),
    avg_days_in_stage = ("days_in_stage", "mean"),
    competitor_rate   = ("competitor_flag", "mean")
).round(3).reset_index()
by_product["segment_type"] = "product_line"
by_product = by_product.rename(columns={"product_line": "segment_value"})

# Benchmark 2: By region
by_region = df.groupby("region").agg(
    total_deals       = ("outcome_binary", "count"),
    win_rate          = ("outcome_binary", "mean"),
    avg_days_closing  = ("total_days_closing", "mean"),
    avg_days_in_stage = ("days_in_stage", "mean"),
    competitor_rate   = ("competitor_flag", "mean")
).round(3).reset_index()
by_region["segment_type"] = "region"
by_region = by_region.rename(columns={"region": "segment_value"})

# Benchmark 3: By deal size category
by_size = df.groupby("deal_size_category").agg(
    total_deals       = ("outcome_binary", "count"),
    win_rate          = ("outcome_binary", "mean"),
    avg_days_closing  = ("total_days_closing", "mean"),
    avg_days_in_stage = ("days_in_stage", "mean"),
    competitor_rate   = ("competitor_flag", "mean")
).round(3).reset_index()
by_size["segment_type"] = "deal_size_category"
by_size = by_size.rename(columns={"deal_size_category": "segment_value"})

# Benchmark 4: By route to market
by_route = df.groupby("route_to_market").agg(
    total_deals       = ("outcome_binary", "count"),
    win_rate          = ("outcome_binary", "mean"),
    avg_days_closing  = ("total_days_closing", "mean"),
    avg_days_in_stage = ("days_in_stage", "mean"),
    competitor_rate   = ("competitor_flag", "mean")
).round(3).reset_index()
by_route["segment_type"] = "route_to_market"
by_route = by_route.rename(columns={"route_to_market": "segment_value"})

# Combine all into one table
benchmarks = pd.concat([by_product, by_region, by_size, by_route], ignore_index=True)
benchmarks.to_sql("segment_benchmarks", engine, if_exists="replace", index=False)
print(benchmarks)
print(f"Saved {len(benchmarks)} benchmark rows to Supabase")
