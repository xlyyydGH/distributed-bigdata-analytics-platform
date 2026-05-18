CREATE DATABASE IF NOT EXISTS bigdata_analytics DEFAULT CHARACTER SET utf8mb4;
USE bigdata_analytics;

CREATE TABLE IF NOT EXISTS daily_overview (
  event_date DATE PRIMARY KEY,
  dau INT,
  sessions INT,
  events INT,
  gmv DECIMAL(18, 2),
  impression INT,
  click INT,
  add_cart INT,
  purchase INT,
  ctr DECIMAL(10, 4),
  cart_rate DECIMAL(10, 4),
  cvr DECIMAL(10, 4),
  arpu DECIMAL(18, 4)
);

CREATE TABLE IF NOT EXISTS category_sales (
  event_date DATE,
  category VARCHAR(64),
  orders INT,
  buyers INT,
  units INT,
  gmv DECIMAL(18, 2),
  avg_order_value DECIMAL(18, 4),
  PRIMARY KEY (event_date, category)
);

CREATE TABLE IF NOT EXISTS top_items (
  item_id VARCHAR(32) PRIMARY KEY,
  item_name VARCHAR(128),
  category VARCHAR(64),
  orders INT,
  buyers INT,
  units INT,
  gmv DECIMAL(18, 2),
  avg_order_value DECIMAL(18, 4)
);

CREATE TABLE IF NOT EXISTS retention (
  cohort_date DATE,
  days_after INT,
  retained_users INT,
  cohort_users INT,
  retention_rate DECIMAL(10, 4),
  PRIMARY KEY (cohort_date, days_after)
);

