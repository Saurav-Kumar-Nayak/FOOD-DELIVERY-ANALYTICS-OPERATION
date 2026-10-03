import os
import json
import sqlite3
import pandas as pd

def generate_kpis_and_powerbi_exports(db_path: str, powerbi_dir: str) -> dict:
    """
    Computes key performance indicators from SQLite Data Warehouse
    and exports Power BI ready Star-Schema CSV files.
    """
    print(f"[KPI ENGINE] Loading data warehouse from: {db_path}")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")

    conn = sqlite3.connect(db_path)
    os.makedirs(powerbi_dir, exist_ok=True)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_csv_path = os.path.join(base_dir, "data", "raw", "food_delivery_raw.csv")

    # 1. Executive KPIs Summary
    kpi_query = """
    SELECT 
        COUNT(DISTINCT r.restaurant_id) AS total_restaurants,
        COUNT(DISTINCT l.city) AS total_cities,
        COUNT(DISTINCT l.country_code) AS total_countries,
        ROUND(AVG(f.aggregate_rating), 2) AS avg_global_rating,
        SUM(f.votes) AS total_votes,
        ROUND(AVG(f.avg_cost_for_two_usd), 2) AS avg_cost_usd,
        ROUND(SUM(f.est_monthly_revenue_usd), 2) AS total_est_monthly_revenue_usd,
        ROUND(100.0 * SUM(r.has_online_delivery) / COUNT(r.restaurant_id), 2) AS online_delivery_pct,
        ROUND(100.0 * SUM(r.has_table_booking) / COUNT(r.restaurant_id), 2) AS table_booking_pct
    FROM dim_restaurants r
    JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id
    JOIN dim_locations l ON r.location_id = l.location_id;
    """
    kpi_df = pd.read_sql_query(kpi_query, conn)
    kpis_dict = kpi_df.to_dict(orient='records')[0]
    print("[KPI ENGINE] Executive KPIs Calculated:")
    for k, v in kpis_dict.items():
        print(f"   - {k}: {v}")

    # 2. Power BI Datasets Export
    print(f"[KPI ENGINE] Exporting Power BI CSVs to: {powerbi_dir}")

    dim_geo = pd.read_sql_query("SELECT * FROM dim_locations", conn)
    dim_geo.to_csv(os.path.join(powerbi_dir, "dim_geography.csv"), index=False)

    dim_rest = pd.read_sql_query("SELECT * FROM dim_restaurants", conn)
    dim_rest.to_csv(os.path.join(powerbi_dir, "dim_restaurant.csv"), index=False)

    fact_perf = pd.read_sql_query("SELECT * FROM fact_restaurant_performance", conn)
    fact_perf.to_csv(os.path.join(powerbi_dir, "fact_orders_summary.csv"), index=False)

    kpi_df.to_csv(os.path.join(powerbi_dir, "kpi_summary_metrics.csv"), index=False)

    cuisine_summary = pd.read_sql_query("SELECT * FROM vw_cuisine_market_share", conn)
    cuisine_summary.to_csv(os.path.join(powerbi_dir, "dim_cuisine_breakdown.csv"), index=False)

    city_summary = pd.read_sql_query("SELECT * FROM vw_city_performance", conn)
    city_summary.to_csv(os.path.join(powerbi_dir, "city_performance_summary.csv"), index=False)

    # Load dynamic raw first 5 preview
    raw_df = pd.read_csv(raw_csv_path, encoding='latin1')
    raw_first_5 = raw_df.head(5).to_dict(orient='records')
    raw_shape = raw_df.shape

    # 3. Build Web Analytics JSON Data Payload
    web_payload = {
        "data_source_info": {
            "filename": "data/raw/food_delivery_raw.csv",
            "grain": "Restaurant-level",
            "records": raw_shape[0],
            "columns": raw_shape[1],
            "last_validated": "2026-10-04",
            "classification": "Observed / Derived / Estimated / Proxy"
        },
        "raw_first_5": raw_first_5,
        "kpis": kpis_dict,
        "city_performance": city_summary.head(15).to_dict(orient='records'),
        "cuisine_market_share": cuisine_summary.head(15).to_dict(orient='records'),
        "price_tier_distribution": pd.read_sql_query(
            "SELECT price_category, COUNT(*) as count, ROUND(AVG(aggregate_rating), 2) as avg_rating FROM dim_restaurants r JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id GROUP BY price_category", conn
        ).to_dict(orient='records'),
        "service_capability_breakdown": pd.read_sql_query(
            "SELECT service_capability, COUNT(*) as count, ROUND(AVG(aggregate_rating), 2) as avg_rating, ROUND(SUM(est_monthly_revenue_usd), 2) as revenue_usd FROM dim_restaurants r JOIN fact_restaurant_performance f ON r.restaurant_id = f.restaurant_id GROUP BY service_capability", conn
        ).to_dict(orient='records')
    }

    payload_path = os.path.join(os.path.dirname(powerbi_dir), "processed", "dashboard_payload.json")
    os.makedirs(os.path.dirname(payload_path), exist_ok=True)
    with open(payload_path, 'w', encoding='utf-8') as f:
        json.dump(web_payload, f, indent=2)
        
    print(f"[KPI ENGINE] Dashboard JSON payload created at: {payload_path}")
    conn.close()
    return web_payload

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_file = os.path.join(base_dir, "data", "food_delivery.db")
    powerbi_folder = os.path.join(base_dir, "data", "power_bi")
    generate_kpis_and_powerbi_exports(db_file, powerbi_folder)
