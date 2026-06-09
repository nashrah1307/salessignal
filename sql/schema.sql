CREATE TABLE deals (
  deal_id                  VARCHAR PRIMARY KEY,
  outcome                  VARCHAR,
  outcome_binary           INT,
  deal_value               FLOAT,
  days_in_stage            FLOAT,
  stage_change_count       FLOAT,
  total_days_closing       FLOAT,
  total_days_qualified     FLOAT,
  product_line             VARCHAR,
  product_group            VARCHAR,
  region                   VARCHAR,
  route_to_market          VARCHAR,
  client_size_revenue      VARCHAR,
  client_size_employees    VARCHAR,
  client_revenue_2yr       FLOAT,
  competitor_type          VARCHAR,
  ratio_identified         FLOAT,
  ratio_validated          FLOAT,
  ratio_qualified          FLOAT,
  deal_size_category       VARCHAR
);
CREATE INDEX ON deals(outcome);
CREATE INDEX ON deals(product_line);
CREATE INDEX ON deals(region);
