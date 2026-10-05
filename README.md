# 🍕 Food Delivery Analytics & Operations Intelligence Platform

An enterprise-grade Analytics and Operations Intelligence platform that transforms raw food delivery data into actionable multi-dimensional insights. The platform features an automated Python ETL data cleaning and domain feature engineering pipeline, an SQLite relational Star-Schema Data Warehouse, an automated KPI Engine, Power BI export datasets, an automated pytest suite, and a dark-navy Enterprise BI Operations Web Dashboard.

[![Vercel Deployment](https://img.shields.io/badge/Vercel-Deployment%20Ready-success?logo=vercel)](https://github.com/Saurav-Kumar-Nayak/FOOD-DELIVERY-ANALYTICS-OPERATION)


---

## 📌 Executive Summary & Metric Classification

> [!IMPORTANT]
> **Dataset Grain Definition**:  
> The dataset represents a **Restaurant-Level Grain** (`9,551` unique restaurant profiles across 141 cities). It is **NOT** an order-level transaction log or customer checkout statement.

### Metric Classification Framework
All business metrics in this platform are strictly classified into four categories:
1. **OBSERVED**: Directly captured raw dataset attributes (e.g., `restaurant_id`, `votes`, `aggregate_rating`, `city`).
2. **DERIVED**: Direct mathematical or categorical calculations (e.g., `online_delivery_pct` = 25.66%, `table_booking_pct` = 12.12%).
3. **ESTIMATED**: Derived calculations based on fixed operational FX baseline assumptions (e.g., `avg_cost_for_two_usd`).
4. **PROXY**: Model-based surrogate metrics representing unobserved metrics (e.g., `est_monthly_revenue_usd` = $15.4M USD).

> [!WARNING]
> **Revenue Disclaimer**:  
> The **"Est. Monthly Revenue (Proxy)"** metric is a mathematical surrogate model derived from vote volume, price category, and cost point. It is intended strictly for relative market performance benchmarking and **MUST NEVER** be cited as actual corporate financial earnings or transaction revenue.

---

## 🏗️ Architecture & Technology Stack

```
                     ┌────────────────────────────────────────┐
                     │ Raw Food Delivery CSV (9,551 Records)  │
                     └───────────────────┬────────────────────┘
                                         │
                                   Python ETL Pipeline
                     ┌───────────────────┴────────────────────┐
                     │ Cleaning & Feature Engineering Engine   │
                     │ (Currency Normalization & Profiling)   │
                     └───────────────────┬────────────────────┘
                                         │
                                 SQLite Data Warehouse
                     ┌───────────────────┴────────────────────┐
                     │ Star Schema DDL & Analytics Views      │
                     │ (dim_restaurants, fact_performance)    │
                     └─────────┬─────────────────────┬────────┘
                               │                     │
                        KPI Engine            Node.js REST API
                     ┌─────────┴─────────┐   ┌───────┴────────────────┐
                     │ Power BI Exporter │   │ Live Dashboard & SQL   │
                     │ (6 Star CSVs)     │   │ Engine (Chart.js Web)  │
                     └───────────────────┘   └────────────────────────┘
```

- **Core Analytics**: Python 3.10+, Pandas, NumPy, SQLite3
- **Database Engine**: Relational SQLite (`data/food_delivery.db`) with Star Schema DDL & Analytical Views
- **Backend API**: Node.js, Express, SQLite Database Driver
- **Frontend Dashboard**: HTML5, Vanilla CSS (Dark Navy Glassmorphism), JavaScript (ES6+), Chart.js
- **Automated Testing**: Pytest (`pytest tests/ -rA`)

---

## 📊 Key Executive KPIs

| KPI Metric | Value | Metric Class | Business Meaning |
| :--- | :--- | :--- | :--- |
| **Total Restaurants** | `9,551` | **OBSERVED** | Count of unique restaurant profile records |
| **Global City Reach** | `141 Cities` (15 Countries)| **OBSERVED** | Geographic market footprint |
| **Avg Global Rating** | `2.67 / 5.0` | **OBSERVED** | Mean customer rating across 1.41M votes |
| **Online Delivery Adoption** | `25.66%` | **DERIVED** | Percentage of listings enabling online delivery |
| **Table Booking Adoption** | `12.12%` | **DERIVED** | Percentage of listings supporting reservations |
| **Global Avg Cost for Two** | `$15.65 USD` | **ESTIMATED** | Mean normalized cost for two (Fixed FX Rates) |
| **Est. Monthly Revenue** | `$15.4M USD` | **PROXY** | Derived synthetic revenue proxy model |

---

## 🗄️ Relational Star Schema Data Warehouse

Located at `data/food_delivery.db`:

- **`dim_locations`**: `location_id` (PK), `city`, `country_code`, `address`, `locality`, `latitude`, `longitude`.
- **`dim_cuisines`**: `cuisine_id` (PK), `cuisine_name`.
- **`dim_restaurants`**: `restaurant_id` (PK), `restaurant_name`, `location_id`, `price_range`, `price_category`, `service_capability`, `has_online_delivery`, `has_table_booking`.
- **`fact_restaurant_performance`**: `fact_id` (PK), `restaurant_id`, `aggregate_rating`, `votes`, `avg_cost_for_two_usd`, `engagement_score`, `est_monthly_orders`, `est_monthly_revenue_usd`.
- **Analytical Views**: `vw_executive_kpis`, `vw_city_performance`, `vw_cuisine_market_share`.

---

## 🚀 How to Run the Platform

### Option 1: Single-Click Launcher (Recommended)
Simply double-click or execute `start_server.bat` (or `start.bat`):
```cmd
start_server.bat
```
*(This automatically runs the ETL data pipeline, builds the SQLite warehouse & KPI engine, launches `http://localhost:3000` in your default browser, and starts the server).*

---

### Option 2: Command Line Startup
```bash
npm start
# or
node server.js
```

---

### Option 3: Manual Step-by-Step Pipeline Execution
```bash
# 1. Clean & Feature Engineer
python src/data_cleaning.py
python src/feature_engineering.py

# 2. Build Database & KPI Payload
python src/db_manager.py
python src/kpi_engine.py

# 3. Launch Web Server
node server.js
```
Open your browser at **`http://localhost:3000`**.

---

## 🧪 Automated Testing

The automated test suite (`tests/`) validates:
- **Cleaned Dataset Integrity**: Validates null handling, schema types, and zero duplicates on `restaurant_id`.
- **Currency Normalization**: Validates 12-currency FX conversions against USD benchmarks.
- **Business Logic Formulas**: Validates adoption percentages, order proxies, and revenue proxy formulas.
- **Python vs. SQL Consistency**: Validates that raw Python calculations match SQLite analytical view outputs down to rounding limits.

To run:
```bash
python -m pytest tests/ -rA
```

---

## 💡 Key Business Insights

1. **Online Delivery Gap**: Only **25.66%** of restaurants currently support online delivery, representing a massive market growth opportunity for platform onboarding.
2. **Rating vs Price Point Alignment**: Premium/Luxury tier restaurants achieve a significantly higher average rating (**3.82 / 5.0**) compared to Budget tier establishments (**1.97 / 5.0**).
3. **Geographic Concentration**: The Top 3 city markets (New Delhi, Gurgaon, and Noida) account for over **68%** of the global estimated revenue proxy volume.

---

## ⚠️ Limitations & Future Improvements

- **Fixed FX Benchmark Rates**: Currency conversions use fixed operational baseline conversion rates rather than real-time dynamic FX feeds.
- **Proxy Revenue Model**: Revenue figures are derived surrogates based on review vote volume and price point. Future iterations could incorporate direct transaction ledgers if payment gateway data becomes available.
- **Real-Time Connectors**: Future improvements include adding Kafka or Webhook connectors for real-time order stream ingestion.

---

## 📄 License & Integrity
All project files are isolated within this workspace. Data and code are validated for production-grade demonstration.
