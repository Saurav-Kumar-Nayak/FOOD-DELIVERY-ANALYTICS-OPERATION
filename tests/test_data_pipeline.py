import os
import sqlite3
import pandas as pd
import numpy as np
import pytest
from src.feature_engineering import CURRENCY_TO_USD

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_CSV = os.path.join(BASE_DIR, "data", "processed", "food_delivery_cleaned.csv")
FEATURED_CSV = os.path.join(BASE_DIR, "data", "processed", "food_delivery_featured.csv")
DB_PATH = os.path.join(BASE_DIR, "data", "food_delivery.db")

def test_cleaned_dataset_integrity():
    assert os.path.exists(CLEANED_CSV), "Cleaned CSV file must exist"
    df = pd.read_csv(CLEANED_CSV)
    assert len(df) == 9551, f"Expected 9551 rows, got {len(df)}"
    assert "restaurant_id" in df.columns, "restaurant_id column must exist"
    assert df["restaurant_id"].nunique() == len(df), "restaurant_id should have zero duplicates"

def test_duplicate_restaurant_handling():
    df_clean = pd.read_csv(CLEANED_CSV)
    df_feat = pd.read_csv(FEATURED_CSV)
    assert df_clean["restaurant_id"].duplicated().sum() == 0, "No duplicate restaurant IDs allowed in cleaned data"
    assert df_feat["restaurant_id"].duplicated().sum() == 0, "No duplicate restaurant IDs allowed in featured data"

def test_currency_conversion():
    df = pd.read_csv(FEATURED_CSV)
    for curr, rate in CURRENCY_TO_USD.items():
        sample = df[df["currency"] == curr]
        if len(sample) > 0:
            row = sample.iloc[0]
            expected_usd = round(row["avg_cost_for_two"] * rate, 2)
            assert row["avg_cost_for_two_usd"] == pytest.approx(expected_usd, abs=0.01), f"FX conversion mismatch for currency {curr}"

def test_adoption_percentages_formulas():
    df = pd.read_csv(FEATURED_CSV)
    total_count = len(df)
    
    delivery_count = df["has_online_delivery"].sum()
    expected_deliv_pct = round(100.0 * delivery_count / total_count, 2)
    assert expected_deliv_pct == 25.66, f"Expected delivery adoption 25.66%, got {expected_deliv_pct}%"
    
    booking_count = df["has_table_booking"].sum()
    expected_book_pct = round(100.0 * booking_count / total_count, 2)
    assert expected_book_pct == 12.12, f"Expected booking adoption 12.12%, got {expected_book_pct}%"

def test_estimated_revenue_formula():
    df = pd.read_csv(FEATURED_CSV)
    # Re-calculate revenue proxy row by row
    multipliers = df["has_online_delivery"].map({1: 1.5, 0: 1.0})
    calc_orders = (df["votes"] * multipliers).round().astype(int)
    calc_revenue = (calc_orders * (df["avg_cost_for_two_usd"] / 2.0)).round(2)
    
    assert (df["est_monthly_orders"] == calc_orders).all(), "Estimated monthly orders formula mismatch"
    assert np.isclose(df["est_monthly_revenue_usd"], calc_revenue, atol=0.01).all(), "Estimated revenue proxy formula mismatch"

def test_database_star_schema():
    assert os.path.exists(DB_PATH), "Database file must exist"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    expected_tables = ["dim_locations", "dim_cuisines", "dim_restaurants", "fact_restaurant_performance"]
    for t in expected_tables:
        assert t in tables, f"Table '{t}' must exist in database"
        
    cursor.execute("SELECT COUNT(*) FROM dim_restaurants;")
    rest_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM fact_restaurant_performance;")
    fact_count = cursor.fetchone()[0]
    
    df_feat = pd.read_csv(FEATURED_CSV)
    assert rest_count == len(df_feat), "dim_restaurants row count must match featured dataframe"
    assert fact_count == len(df_feat), "fact_restaurant_performance row count must match featured dataframe"
    
    conn.close()
