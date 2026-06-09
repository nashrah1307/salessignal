import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql://postgres:postgres123@localhost:5432/postgres"

df = pd.read_csv("data/sales.csv")

# Rename every column to the clean names used across the project
df = df.rename(columns={
    "Opportunity Number":                      "deal_id",
    "Opportunity Result":                      "outcome",
    "Opportunity Amount USD":                  "deal_value",
    "Elapsed Days In Sales Stage":             "days_in_stage",
    "Sales Stage Change Count":                "stage_change_count",
    "Total Days Identified Through Closing":   "total_days_closing",
    "Total Days Identified Through Qualified": "total_days_qualified",
    "Supplies Subgroup":                       "product_line",
    "Supplies Group":                          "product_group",
    "Region":                                  "region",
    "Route To Market":                         "route_to_market",
    "Client Size By Revenue":                  "client_size_revenue",
    "Client Size By Employee Count":           "client_size_employees",
    "Revenue From Client Past Two Years":      "client_revenue_2yr",
    "Competitor Type":                         "competitor_type",
    "Ratio Days Identified To Total Days":     "ratio_identified",
    "Ratio Days Validated To Total Days":      "ratio_validated",
    "Ratio Days Qualified To Total Days":      "ratio_qualified",
    "Deal Size Category":                      "deal_size_category"
})

# Drop rows missing the two most critical columns
df.dropna(subset=["outcome", "deal_value"], inplace=True)

# Create binary outcome: 1 = Won, 0 = Lost
# First print what values exist in outcome column
print("Outcome values:", df["outcome"].value_counts())
df["outcome_binary"] = (df["outcome"] == "Won").astype(int)

engine = create_engine(DB_URL)
df.to_sql("deals", engine, if_exists="replace", index=False)
print(f"Done — {len(df)} rows loaded into Supabase")
