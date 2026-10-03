import os
import pandas as pd
import numpy as np

def clean_food_delivery_data(raw_path: str, output_path: str) -> pd.DataFrame:
    """
    Data Cleaning Pipeline for Food Delivery Dataset.
    Standardizes schema, handles missing values, normalizes binary flags, and trims string fields.
    """
    print(f"[DATA CLEANING] Loading raw data from: {raw_path}")
    df = pd.read_csv(raw_path)
    
    # 1. Standardize Column Names
    raw_cols = df.columns.tolist()
    clean_cols = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in raw_cols]
    df.columns = clean_cols
    print(f"[DATA CLEANING] Columns standardized: {len(df.columns)} columns")
    
    # Rename specific columns if needed
    rename_dict = {
        'average_cost_for_two': 'avg_cost_for_two'
    }
    df.rename(columns=rename_dict, inplace=True)
    
    # 2. String Trimming & Formatting
    string_cols = ['restaurant_name', 'city', 'address', 'locality', 'locality_verbose', 'cuisines', 'currency', 'rating_color', 'rating_text']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({'nan': np.nan, 'None': np.nan, '': np.nan})

    # 3. Handle Missing Values
    if 'cuisines' in df.columns:
        df['cuisines'] = df['cuisines'].fillna('Unknown / Multi-Cuisine')
        
    # 4. Standardize Binary Flags (Yes/No -> 1/0)
    flag_cols = ['has_table_booking', 'has_online_delivery', 'is_delivering_now', 'switch_to_order_menu']
    for col in flag_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
            df[col] = df[col].map({'yes': 1, 'no': 0, '1': 1, '0': 0, 'true': 1, 'false': 0}).fillna(0).astype(int)
            
    # 5. Type Conversions & Numeric Sanitization
    df['restaurant_id'] = pd.to_numeric(df['restaurant_id'], errors='coerce').astype('int64')
    df['country_code'] = pd.to_numeric(df['country_code'], errors='coerce').fillna(0).astype('int64')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce').fillna(0.0)
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce').fillna(0.0)
    df['avg_cost_for_two'] = pd.to_numeric(df['avg_cost_for_two'], errors='coerce').fillna(0.0)
    df['price_range'] = pd.to_numeric(df['price_range'], errors='coerce').fillna(1).astype(int)
    df['aggregate_rating'] = pd.to_numeric(df['aggregate_rating'], errors='coerce').fillna(0.0)
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)

    # 6. Deduplication
    initial_len = len(df)
    df.drop_duplicates(subset=['restaurant_id'], keep='first', inplace=True)
    dedup_count = initial_len - len(df)
    if dedup_count > 0:
        print(f"[DATA CLEANING] Removed {dedup_count} duplicate restaurant records.")

    # 7. Save Cleaned Dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[DATA CLEANING] Cleaned data saved to {output_path} with {len(df)} rows and {len(df.columns)} columns.")
    return df

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_file = os.path.join(base_dir, "data", "raw", "food_delivery_raw.csv")
    cleaned_file = os.path.join(base_dir, "data", "processed", "food_delivery_cleaned.csv")
    clean_food_delivery_data(raw_file, cleaned_file)
