-- Food Delivery Analytics & Operations Intelligence Query Suite

-- 1. High-Performance Restaurant Ranking by City (Window Function ROW_NUMBER & RANK)
WITH RankedRestaurants AS (
    SELECT 
        l.city,
        r.restaurant_id,
        r.restaurant_name,
        r.primary_cuisine,
        f.aggregate_rating,
        f.votes,
        f.engagement_score,
        f.avg_cost_for_two_usd,
        DENSE_RANK() OVER (PARTITION BY l.city ORDER BY f.engagement_score DESC) AS city_rank
    FROM dim_restaurants r
    JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id
    JOIN dim_locations l ON r.location_id = l.location_id
    WHERE f.aggregate_rating >= 4.0
)
SELECT city, city_rank, restaurant_name, primary_cuisine, aggregate_rating, votes, engagement_score
FROM RankedRestaurants
WHERE city_rank <= 3
ORDER BY city, city_rank;

-- 2. Online Delivery Market Penetration & Rating Gap Analysis by Price Tier
SELECT 
    r.price_category,
    COUNT(r.restaurant_id) AS total_restaurants,
    SUM(CASE WHEN r.has_online_delivery = 1 THEN 1 ELSE 0 END) AS delivery_enabled_count,
    ROUND(100.0 * SUM(r.has_online_delivery) / COUNT(r.restaurant_id), 2) AS delivery_penetration_pct,
    ROUND(AVG(CASE WHEN r.has_online_delivery = 1 THEN f.aggregate_rating ELSE NULL END), 2) AS avg_rating_with_delivery,
    ROUND(AVG(CASE WHEN r.has_online_delivery = 0 THEN f.aggregate_rating ELSE NULL END), 2) AS avg_rating_without_delivery,
    ROUND(AVG(CASE WHEN r.has_online_delivery = 1 THEN f.aggregate_rating ELSE NULL END) - 
          AVG(CASE WHEN r.has_online_delivery = 0 THEN f.aggregate_rating ELSE NULL END), 2) AS rating_delta
FROM dim_restaurants r
JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id
GROUP BY r.price_category
ORDER BY r.price_category;

-- 3. Customer Engagement Percentile Segmentation (NTILE Window Function)
WITH EngagementQuartiles AS (
    SELECT 
        r.restaurant_id,
        r.restaurant_name,
        l.city,
        f.engagement_score,
        f.est_monthly_revenue_usd,
        NTILE(4) OVER (ORDER BY f.engagement_score DESC) AS engagement_quartile
    FROM dim_restaurants r
    JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id
    JOIN dim_locations l ON r.location_id = l.location_id
    WHERE f.votes > 0
)
SELECT 
    CASE engagement_quartile 
        WHEN 1 THEN 'Q1 - Top 25% High Engagement'
        WHEN 2 THEN 'Q2 - Upper-Mid Engagement'
        WHEN 3 THEN 'Q3 - Lower-Mid Engagement'
        WHEN 4 THEN 'Q4 - Bottom 25% Low Engagement'
    END AS quartile_label,
    COUNT(restaurant_id) AS restaurant_count,
    ROUND(AVG(engagement_score), 2) AS avg_engagement_score,
    ROUND(AVG(est_monthly_revenue_usd), 2) AS avg_monthly_revenue_usd,
    ROUND(SUM(est_monthly_revenue_usd), 2) AS total_quartile_revenue_usd
FROM EngagementQuartiles
GROUP BY engagement_quartile
ORDER BY engagement_quartile;

-- 4. Cuisine Density & Unit Economics Matrix
SELECT 
    r.primary_cuisine,
    COUNT(r.restaurant_id) AS total_restaurants,
    ROUND(AVG(f.avg_cost_for_two_usd), 2) AS avg_cost_usd,
    ROUND(AVG(f.aggregate_rating), 2) AS avg_rating,
    SUM(f.votes) AS total_votes,
    ROUND(AVG(f.votes), 1) AS avg_votes_per_rest,
    ROUND(100.0 * SUM(r.has_online_delivery) / COUNT(r.restaurant_id), 1) AS online_delivery_pct
FROM dim_restaurants r
JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id
GROUP BY r.primary_cuisine
HAVING COUNT(r.restaurant_id) >= 20
ORDER BY avg_votes_per_rest DESC;

-- 5. Delivery Capability vs Table Booking Operational Synergy CTE
WITH ServiceMatrix AS (
    SELECT 
        r.service_capability,
        COUNT(r.restaurant_id) AS total_count,
        AVG(f.aggregate_rating) AS avg_rating,
        AVG(f.votes) AS avg_votes,
        AVG(f.avg_cost_for_two_usd) AS avg_cost_usd,
        SUM(f.est_monthly_revenue_usd) AS est_total_revenue
    FROM dim_restaurants r
    JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id
    GROUP BY r.service_capability
)
SELECT 
    service_capability,
    total_count,
    ROUND(avg_rating, 2) AS avg_rating,
    ROUND(avg_votes, 1) AS avg_votes,
    ROUND(avg_cost_usd, 2) AS avg_cost_usd,
    ROUND(est_total_revenue, 2) AS est_total_revenue_usd,
    ROUND(100.0 * total_count / (SELECT SUM(total_count) FROM ServiceMatrix), 2) AS segment_share_pct
FROM ServiceMatrix
ORDER BY est_total_revenue DESC;
