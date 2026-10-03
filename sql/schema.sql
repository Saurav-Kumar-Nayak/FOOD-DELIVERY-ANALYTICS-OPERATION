-- Food Delivery Analytics Data Warehouse Schema DDL

DROP TABLE IF EXISTS fact_restaurant_performance;
DROP TABLE IF EXISTS dim_restaurants;
DROP TABLE IF EXISTS dim_locations;
DROP TABLE IF EXISTS dim_cuisines;
DROP VIEW IF EXISTS vw_executive_kpis;
DROP VIEW IF EXISTS vw_city_performance;
DROP VIEW IF EXISTS vw_cuisine_market_share;

-- Dimension: Locations
CREATE TABLE dim_locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    country_code INTEGER NOT NULL,
    address TEXT,
    locality TEXT,
    longitude REAL,
    latitude REAL
);

-- Dimension: Cuisines
CREATE TABLE dim_cuisines (
    cuisine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cuisine_name TEXT UNIQUE NOT NULL
);

-- Dimension: Restaurants
CREATE TABLE dim_restaurants (
    restaurant_id INTEGER PRIMARY KEY,
    restaurant_name TEXT NOT NULL,
    location_id INTEGER,
    primary_cuisine TEXT,
    cuisines TEXT,
    price_range INTEGER,
    price_category TEXT,
    has_table_booking INTEGER,
    has_online_delivery INTEGER,
    is_delivering_now INTEGER,
    service_capability TEXT,
    FOREIGN KEY (location_id) REFERENCES dim_locations(location_id)
);

-- Fact Table: Restaurant Performance & Metrics
CREATE TABLE fact_restaurant_performance (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL,
    avg_cost_for_two REAL,
    currency TEXT,
    avg_cost_for_two_usd REAL,
    aggregate_rating REAL,
    rating_color TEXT,
    rating_text TEXT,
    rating_group TEXT,
    votes INTEGER,
    engagement_score REAL,
    est_monthly_orders INTEGER,
    est_monthly_revenue_usd REAL,
    FOREIGN KEY (restaurant_id) REFERENCES dim_restaurants(restaurant_id)
);

-- Executive KPI View
CREATE VIEW vw_executive_kpis AS
SELECT 
    COUNT(DISTINCT r.restaurant_id) AS total_restaurants,
    COUNT(DISTINCT l.city) AS total_cities,
    ROUND(AVG(f.aggregate_rating), 2) AS global_avg_rating,
    SUM(f.votes) AS total_customer_votes,
    ROUND(AVG(f.avg_cost_for_two_usd), 2) AS global_avg_cost_usd,
    ROUND(SUM(f.est_monthly_revenue_usd), 2) AS total_est_monthly_revenue_usd,
    ROUND(100.0 * SUM(r.has_online_delivery) / COUNT(*), 2) AS online_delivery_adoption_pct,
    ROUND(100.0 * SUM(r.has_table_booking) / COUNT(*), 2) AS table_booking_adoption_pct
FROM dim_restaurants r
JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id
JOIN dim_locations l ON r.location_id = l.location_id;

-- City Level Analytical View
CREATE VIEW vw_city_performance AS
SELECT 
    l.city,
    COUNT(r.restaurant_id) AS restaurant_count,
    ROUND(AVG(f.aggregate_rating), 2) AS avg_rating,
    SUM(f.votes) AS total_votes,
    ROUND(AVG(f.avg_cost_for_two_usd), 2) AS avg_cost_usd,
    ROUND(100.0 * SUM(r.has_online_delivery) / COUNT(*), 2) AS delivery_adoption_pct,
    ROUND(SUM(f.est_monthly_revenue_usd), 2) AS city_est_revenue_usd
FROM dim_restaurants r
JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id
JOIN dim_locations l ON r.location_id = l.location_id
GROUP BY l.city
ORDER BY restaurant_count DESC;

-- Cuisine Market Share View
CREATE VIEW vw_cuisine_market_share AS
SELECT 
    r.primary_cuisine,
    COUNT(r.restaurant_id) AS restaurant_count,
    SUM(f.votes) AS total_votes,
    ROUND(AVG(f.aggregate_rating), 2) AS avg_rating,
    ROUND(AVG(f.avg_cost_for_two_usd), 2) AS avg_cost_usd,
    ROUND(SUM(f.est_monthly_revenue_usd), 2) AS cuisine_est_revenue_usd
FROM dim_restaurants r
JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id
GROUP BY r.primary_cuisine
ORDER BY restaurant_count DESC;
