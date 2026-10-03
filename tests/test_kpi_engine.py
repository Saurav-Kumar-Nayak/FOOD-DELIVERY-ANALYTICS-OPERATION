import os
import json
import sqlite3
import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURED_CSV = os.path.join(BASE_DIR, "data", "processed", "food_delivery_featured.csv")
DB_PATH = os.path.join(BASE_DIR, "data", "food_delivery.db")
POWERBI_DIR = os.path.join(BASE_DIR, "data", "power_bi")
PAYLOAD_JSON = os.path.join(BASE_DIR, "data", "processed", "dashboard_payload.json")

def test_powerbi_exports_exist():
    expected_files = [
        "dim_geography.csv",
        "dim_restaurant.csv",
        "fact_orders_summary.csv",
        "kpi_summary_metrics.csv",
        "dim_cuisine_breakdown.csv",
        "city_performance_summary.csv"
    ]
    for filename in expected_files:
        filepath = os.path.join(POWERBI_DIR, filename)
        assert os.path.exists(filepath), f"Power BI file '{filename}' should exist"
        df = pd.read_csv(filepath)
        assert len(df) > 0, f"Power BI file '{filename}' should not be empty"

def test_python_vs_sql_kpi_consistency():
    # 1. Independent Python Calculation directly from featured CSV
    df = pd.read_csv(FEATURED_CSV)
    py_total_restaurants = len(df)
    py_total_cities = df["city"].nunique()
    py_avg_rating = round(df["aggregate_rating"].mean(), 2)
    py_total_votes = int(df["votes"].sum())
    py_avg_cost_usd = round(df["avg_cost_for_two_usd"].mean(), 2)
    py_total_est_revenue = round(df["est_monthly_revenue_usd"].sum(), 2)
    py_deliv_pct = round(100.0 * df["has_online_delivery"].sum() / py_total_restaurants, 2)
    py_book_pct = round(100.0 * df["has_table_booking"].sum() / py_total_restaurants, 2)

    # 2. SQLite Database Calculation
    conn = sqlite3.connect(DB_PATH)
    sql_df = pd.read_sql_query("SELECT * FROM vw_executive_kpis", conn)
    conn.close()
    sql_row = sql_df.iloc[0]

    # Compare Python vs SQL
    assert py_total_restaurants == sql_row["total_restaurants"], "Python vs SQL total_restaurants mismatch"
    assert py_total_cities == sql_row["total_cities"], "Python vs SQL total_cities mismatch"
    assert py_avg_rating == sql_row["global_avg_rating"], "Python vs SQL global_avg_rating mismatch"
    assert py_total_votes == sql_row["total_customer_votes"], "Python vs SQL total_customer_votes mismatch"
    assert py_avg_cost_usd == sql_row["global_avg_cost_usd"], "Python vs SQL global_avg_cost_usd mismatch"
    assert py_total_est_revenue == sql_row["total_est_monthly_revenue_usd"], "Python vs SQL total_est_monthly_revenue_usd mismatch"
    assert py_deliv_pct == sql_row["online_delivery_adoption_pct"], "Python vs SQL online_delivery_adoption_pct mismatch"
    assert py_book_pct == sql_row["table_booking_adoption_pct"], "Python vs SQL table_booking_adoption_pct mismatch"

def test_dashboard_payload_consistency():
    assert os.path.exists(PAYLOAD_JSON), "Dashboard payload JSON must exist"
    with open(PAYLOAD_JSON, 'r', encoding='utf-8') as f:
        payload = json.load(f)
        
    kpis = payload["kpis"]
    assert kpis["total_restaurants"] == 9551
    assert kpis["online_delivery_pct"] == 25.66
    assert kpis["table_booking_pct"] == 12.12
    assert kpis["avg_global_rating"] == 2.67
