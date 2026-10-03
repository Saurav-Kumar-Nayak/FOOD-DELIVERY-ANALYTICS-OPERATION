# Food Delivery Analytics & Operations Intelligence - Data Source Reconciliation Report

**Report Date**: 2026-10-04  
**Project Workspace**: `C:\Users\nayak\Downloads\project\FOOD DELIVERY ANALYTICS & OPERATIONS INTELLIGENCE`

---

## 1. Source Data Specification & Verification

| Property | Value | Status |
| :--- | :--- | :--- |
| **Actual Source File Path** | `data/raw/food_delivery_raw.csv` | **VERIFIED PHYSICAL FILE** |
| **Row Count** | `9,551` | **RECONCILED 100%** |
| **Column Count** | `21` | **RECONCILED 100%** |
| **Dataset Grain** | **Restaurant-Level** | **VERIFIED (1 row = 1 restaurant)** |
| **Primary Key / Identifier** | `Restaurant ID` (`restaurant_id`) | **0 DUPLICATES** |
| **Cities Covered** | `141 Cities` (15 Countries) | **VERIFIED** |

---

## 2. End-to-End Data Lineage Pipeline Map

```
[Raw CSV: data/raw/food_delivery_raw.csv] (9,551 rows x 21 cols)
    │
    ▼ (src/data_cleaning.py)
[Cleaned CSV: data/processed/food_delivery_cleaned.csv] (9,551 rows x 21 cols)
    │
    ▼ (src/feature_engineering.py)
[Featured CSV: data/processed/food_delivery_featured.csv] (9,551 rows x 30 cols)
    │
    ▼ (src/db_manager.py)
[SQLite Data Warehouse: data/food_delivery.db]
    ├── dim_locations (141 cities)
    ├── dim_cuisines (143 cuisines)
    ├── dim_restaurants (9,551 rows)
    └── fact_restaurant_performance (9,551 rows)
    │
    ▼ (src/kpi_engine.py)
[Web JSON Payload: data/processed/dashboard_payload.json] + [Power BI Star Schema CSVs]
    │
    ▼ (server.js & public/app.js)
[Enterprise Web Operations Portal (http://localhost:3000)]
```

---

## 3. Numeric Reconciliation Matrix

| Metric Name | Source Calculation | SQLite Database Result | Dashboard Display | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Total Restaurants** | `COUNT(DISTINCT restaurant_id)` | `9,551` | `9,551` | **MATCH** |
| **Total Cities** | `COUNT(DISTINCT city)` | `141` | `141` | **MATCH** |
| **Total Countries** | `COUNT(DISTINCT country_code)` | `15` | `15` | **MATCH** |
| **Avg Global Rating** | `AVG(aggregate_rating)` | `2.67` | `2.67 / 5.0` | **MATCH** |
| **Total Customer Votes** | `SUM(votes)` | `1,412,416` | `1.41M Votes` | **MATCH** |
| **Avg Cost USD** | `AVG(avg_cost_for_two_usd)` | `$15.65` | `$15.65` | **MATCH** |
| **Online Delivery Adoption** | `(SUM(has_online_delivery) / COUNT(*)) * 100` | `25.66%` | `25.66%` | **MATCH** |
| **Table Booking Adoption** | `(SUM(has_table_booking) / COUNT(*)) * 100` | `12.12%` | `12.12%` | **MATCH** |
| **Est. Monthly Revenue (Proxy)**| `SUM(est_monthly_revenue_usd)` | `$15,391,732.18` | `$15.4M` | **MATCH** |

---

## 4. Audit & Verification Findings

- **Order-Level Terminology Audit**: Scanned all codebase, SQL, tests, and documentation files for fake order-level metrics (`order_id`, `customer_id`, `delivery_delay`, `churn`). **0 instances found**.
- **Revenue Representation**: Revenue is explicitly labeled as **`Est. Monthly Revenue (Proxy)`** across all UI cards, headers, SQL presets, and reports.
- **Dynamic Source Preview**: Integrated dynamic Data Source & Methodology panel and a live 5-row raw preview directly fed from `data/raw/food_delivery_raw.csv`.
- **Test Suite Results**: `python -m pytest tests/ -rA` passed `9/9` with 100% success rate.

---

## 5. Final Reconciliation Status

**DATA LINEAGE RECONCILIATION**: **PASS**  
**DASHBOARD SOURCE TRANSPARENCY**: **PASS**  
**PROJECT STATUS**: **RECONCILED & FROZEN**
