import os
import pandas as pd
import numpy as np

# Currency conversion rates to USD
CURRENCY_TO_USD = {
    'Indian Rupees(Rs.)': 0.012,
    'Dollar($)': 1.0,
    'Pounds(£)': 1.30,
    'Brazilian Real(R$)': 0.18,
    'Emirati Diram(AED)': 0.27,
    'Rand(R)': 0.055,
    'NewZealand($)': 0.60,
    'Turkish Lira(TL)': 0.029,
    'Botswana Pula(P)': 0.074,
    'Indonesian Rupiah(IDR)': 0.000065,
    'Qatari Rial(QR)': 0.27,
    'Sri Lankan Rupee(LKR)': 0.0033
}

def engineer_features(cleaned_csv_path: str, output_csv_path: str) -> pd.DataFrame:
    """
    Applies domain-specific feature engineering to the cleaned food delivery dataset.
    Engineers cost normalization, primary cuisine, service capabilities, customer engagement,
    and rating performance groups.
    """
    print(f"[FEATURE ENGINEERING] Loading cleaned data from: {cleaned_csv_path}")
    df = pd.read_csv(cleaned_csv_path)

    # 1. Primary Cuisine & Cuisine Count
    def get_primary_cuisine(cuisines_str):
        if pd.isna(cuisines_str) or str(cuisines_str).strip() == '':
            return 'Unknown'
        parts = [c.strip() for c in str(cuisines_str).split(',')]
        return parts[0] if len(parts) > 0 else 'Unknown'

    def get_cuisine_count(cuisines_str):
        if pd.isna(cuisines_str) or str(cuisines_str).strip() == '':
            return 0
        return len([c.strip() for c in str(cuisines_str).split(',') if c.strip()])

    df['primary_cuisine'] = df['cuisines'].apply(get_primary_cuisine)
    df['cuisine_count'] = df['cuisines'].apply(get_cuisine_count)

    # 2. Currency Normalization to USD
    def convert_to_usd(row):
        curr = row.get('currency', 'Dollar($)')
        cost = row.get('avg_cost_for_two', 0.0)
        rate = CURRENCY_TO_USD.get(curr, 1.0)
        return round(cost * rate, 2)

    df['avg_cost_for_two_usd'] = df.apply(convert_to_usd, axis=1)

    # 3. Price Category Labeling
    price_map = {
        1: '1 - Budget',
        2: '2 - Economy',
        3: '3 - Mid-High',
        4: '4 - Premium/Luxury'
    }
    df['price_category'] = df['price_range'].map(price_map).fillna('1 - Budget')

    # 4. Service Capability Classification
    def categorize_service(row):
        deliv = row.get('has_online_delivery', 0)
        book = row.get('has_table_booking', 0)
        if deliv == 1 and book == 1:
            return 'Full-Service (Online & Booking)'
        elif deliv == 1:
            return 'Delivery-Centric'
        elif book == 1:
            return 'Dine-In & Reservation'
        else:
            return 'Standard Dine-In Only'

    df['service_capability'] = df.apply(categorize_service, axis=1)

    # 5. Rating Group Classification
    def group_rating(rating):
        if pd.isna(rating) or rating == 0:
            return 'Unrated'
        elif rating >= 4.5:
            return '4.5 - 5.0 (Top Tier)'
        elif rating >= 4.0:
            return '4.0 - 4.4 (High)'
        elif rating >= 3.0:
            return '3.0 - 3.9 (Moderate)'
        else:
            return '< 3.0 (Low)'

    df['rating_group'] = df['aggregate_rating'].apply(group_rating)

    # 6. Customer Engagement Score & Revenue Proxy
    df['engagement_score'] = np.round(np.log1p(df['votes']) * df['aggregate_rating'], 2)
    
    # Revenue proxy calculation
    # Estimated monthly orders proxy = votes * (1.5 if online delivery else 1.0)
    multiplier = df['has_online_delivery'].map({1: 1.5, 0: 1.0})
    df['est_monthly_orders'] = np.round(df['votes'] * multiplier).astype(int)
    df['est_monthly_revenue_usd'] = np.round(df['est_monthly_orders'] * (df['avg_cost_for_two_usd'] / 2.0), 2)

    # 7. Save Featured Dataset
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    print(f"[FEATURE ENGINEERING] Featured data successfully saved to: {output_csv_path}")
    print(f"[FEATURE ENGINEERING] Total records: {len(df)}, Total columns: {len(df.columns)}")
    return df

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cleaned_file = os.path.join(base_dir, "data", "processed", "food_delivery_cleaned.csv")
    featured_file = os.path.join(base_dir, "data", "processed", "food_delivery_featured.csv")
    engineer_features(cleaned_file, featured_file)
