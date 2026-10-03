import os
import sqlite3
import pandas as pd

def build_database(csv_path: str, db_path: str, schema_path: str):
    """
    Ingests featured dataset, populates Star Schema SQLite database, and creates analytical views.
    """
    print(f"[DB MANAGER] Initializing database at: {db_path}")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Featured CSV not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Read and execute Schema DDL
    print(f"[DB MANAGER] Executing schema DDL from: {schema_path}")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()

    # 2. Populate dim_locations
    print("[DB MANAGER] Populating dim_locations...")
    location_df = df[['city', 'country_code', 'address', 'locality', 'longitude', 'latitude']].drop_duplicates().reset_index(drop=True)
    location_df.insert(0, 'location_id', range(1, 1 + len(location_df)))
    location_df.to_sql('dim_locations', conn, if_exists='append', index=False)

    # 3. Populate dim_cuisines
    print("[DB MANAGER] Populating dim_cuisines...")
    cuisines_set = set()
    for item in df['cuisines'].dropna():
        for c in str(item).split(','):
            c_clean = c.strip()
            if c_clean:
                cuisines_set.add(c_clean)
    cuisines_df = pd.DataFrame(sorted(list(cuisines_set)), columns=['cuisine_name'])
    cuisines_df.insert(0, 'cuisine_id', range(1, 1 + len(cuisines_df)))
    cuisines_df.to_sql('dim_cuisines', conn, if_exists='append', index=False)

    # 4. Map location_id back to main dataframe
    merged_df = df.merge(
        location_df[['location_id', 'city', 'country_code', 'address', 'locality', 'longitude', 'latitude']],
        on=['city', 'country_code', 'address', 'locality', 'longitude', 'latitude'],
        how='left'
    )

    # 5. Populate dim_restaurants
    print("[DB MANAGER] Populating dim_restaurants...")
    restaurants_df = merged_df[[
        'restaurant_id', 'restaurant_name', 'location_id', 'primary_cuisine',
        'cuisines', 'price_range', 'price_category', 'has_table_booking',
        'has_online_delivery', 'is_delivering_now', 'service_capability'
    ]].drop_duplicates(subset=['restaurant_id'])
    restaurants_df.to_sql('dim_restaurants', conn, if_exists='append', index=False)

    # 6. Populate fact_restaurant_performance
    print("[DB MANAGER] Populating fact_restaurant_performance...")
    fact_df = merged_df[[
        'restaurant_id', 'avg_cost_for_two', 'currency', 'avg_cost_for_two_usd',
        'aggregate_rating', 'rating_color', 'rating_text', 'rating_group',
        'votes', 'engagement_score', 'est_monthly_orders', 'est_monthly_revenue_usd'
    ]]
    fact_df.to_sql('fact_restaurant_performance', conn, if_exists='append', index=False)

    conn.commit()
    print("[DB MANAGER] Database population complete!")

    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"[DB MANAGER] Tables created: {tables}")
    
    # Test Executive View
    cursor.execute("SELECT * FROM vw_executive_kpis;")
    kpis = cursor.fetchone()
    print(f"[DB MANAGER] Executive KPIs loaded: Total Rest={kpis[0]}, Cities={kpis[1]}, Avg Rating={kpis[2]}, Total Votes={kpis[3]}")

    conn.close()
    return db_path

def execute_analytics_queries(db_path: str, queries_path: str):
    """
    Executes sample analytical queries against the database and prints summary results.
    """
    print(f"[DB MANAGER] Running analytics queries from: {queries_path}")
    conn = sqlite3.connect(db_path)
    with open(queries_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Split by semicolon
    queries = [q.strip() for q in sql_content.split(';') if q.strip()]
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query #{i} Execution ---")
        try:
            res_df = pd.read_sql_query(query, conn)
            print(res_df.head(5).to_string())
        except Exception as e:
            print(f"Error executing Query #{i}: {e}")
            
    conn.close()

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    featured_file = os.path.join(base_dir, "data", "processed", "food_delivery_featured.csv")
    db_file = os.path.join(base_dir, "data", "food_delivery.db")
    schema_file = os.path.join(base_dir, "sql", "schema.sql")
    queries_file = os.path.join(base_dir, "sql", "analytics_queries.sql")

    build_database(featured_file, db_file, schema_file)
    execute_analytics_queries(db_file, queries_file)
