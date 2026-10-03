# Food Delivery Analytics & Operations Intelligence - Final Data & Business Logic Audit Report

**Audit Completion Date**: 2026-10-04  
**Audit Scope**: Strict Data Quality, Metric Classification, KPI Formula Traceability, Currency Normalization, and Python-vs-SQL Validation inside `FOOD DELIVERY ANALYTICS & OPERATIONS INTELLIGENCE`.

---

## 1. Dataset Grain & Reality Check
- **Dataset Entity Level**: Restaurant-Level Grain.
- **Verified Raw Row Count**: `9,551` rows, `21` columns.
- **Verified Cleaned Row Count**: `9,551` rows, `21` columns.
- **Verified Featured Row Count**: `9,551` rows, `30` columns.
- **Unique Restaurant Identifier**: `restaurant_id` (`9,551` unique IDs out of `9,551` rows — `0` duplicates).
- **Reality Determination**: The dataset represents **restaurant profiles and operational capabilities**, NOT individual customer order receipts or transaction ledgers.

---

## 2. KPI Traceability Matrix

| KPI Display Name | Source Column(s) | Mathematical Formula / Aggregation | Classification | Business Meaning |
| :--- | :--- | :--- | :--- | :--- |
| **Total Restaurants** | `restaurant_id` | `COUNT(DISTINCT restaurant_id)` | **OBSERVED** | Total number of unique restaurant profiles in the data warehouse |
| **Total Cities** | `city` | `COUNT(DISTINCT city)` | **OBSERVED** | Total unique geographic city markets covered |
| **Total Countries** | `country_code` | `COUNT(DISTINCT country_code)` | **OBSERVED** | Total unique country jurisdictions represented |
| **Average Global Rating** | `aggregate_rating` | `AVG(aggregate_rating)` | **OBSERVED** | Unweighted average rating across all restaurants |
| **Total Customer Votes** | `votes` | `SUM(votes)` | **OBSERVED** | Total accumulated review votes across all listings |
| **Global Avg Cost for Two**| `avg_cost_for_two_usd` | `AVG(avg_cost_for_two_usd)` | **ESTIMATED** | Mean estimated cost for two normalized to USD using fixed FX rates |
| **Online Delivery Adoption**| `has_online_delivery` | `(SUM(has_online_delivery) / COUNT(*)) * 100` | **DERIVED** | Percentage of total restaurants offering online delivery |
| **Table Booking Adoption** | `has_table_booking` | `(SUM(has_table_booking) / COUNT(*)) * 100` | **DERIVED** | Percentage of total restaurants supporting table reservations |
| **Est. Monthly Revenue** | `votes`, `has_online_delivery`, `avg_cost_for_two_usd` | `SUM(round(votes * (1.5 if delivery else 1.0)) * (avg_cost_for_two_usd / 2))` | **PROXY** | Derived revenue proxy for market segmentation (NOT actual financial ledger) |

---

## 3. Metric Classification Audit

Every metric across the application, database, and web dashboard is explicitly classified as:
- **OBSERVED**: Raw data fields (e.g., `restaurant_id`, `votes`, `aggregate_rating`, `city`).
- **DERIVED**: Direct mathematical ratios/groupings (e.g., `online_delivery_pct` = 25.66%, `table_booking_pct` = 12.12%).
- **ESTIMATED**: Derived values depending on fixed baseline assumptions (e.g., `avg_cost_for_two_usd`).
- **PROXY**: Surrogate models for unobserved quantities (e.g., `est_monthly_revenue_usd` = $15.4M USD).

> [!IMPORTANT]
> All UI labels have been audited and updated to explicitly state **"(Observed)"**, **"(Derived)"**, or **"(Proxy)"** (e.g. *"Est. Monthly Revenue (Proxy)"*).

---

## 4. KPI Formula & Cross-Engine Validation

All primary KPIs were independently calculated across three independent layers (Raw Python Dataframe, SQLite Relational Engine DDL View, and Node API JSON Payload):

| KPI Metric | Raw Python Calculation | SQLite View (`vw_executive_kpis`) | API Payload (`dashboard_payload.json`) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Total Restaurants** | `9,551` | `9,551` | `9,551` | **MATCH** |
| **Total Cities** | `141` | `141` | `141` | **MATCH** |
| **Global Avg Rating** | `2.67` | `2.67` | `2.67` | **MATCH** |
| **Total Customer Votes** | `1,498,061` | `1,498,061` | `1,498,061` | **MATCH** |
| **Avg Cost for Two (USD)** | `$15.65` | `$15.65` | `$15.65` | **MATCH** |
| **Online Delivery Adoption** | `25.66%` | `25.66%` | `25.66%` | **MATCH** |
| **Table Booking Adoption** | `12.12%` | `12.12%` | `12.12%` | **MATCH** |
| **Est. Monthly Revenue (USD)** | `$15,404,364.57` | `$15,404,364.57` | `$15,404,364.57` | **MATCH** |

---

## 5. Currency Normalization Validation
- **Methodology**: Applied fixed operational FX baseline conversion factors across 12 currencies.
- **Conversion Rates**:
  - `Indian Rupees(Rs.)`: `0.012` (8,652 records)
  - `Dollar($)`: `1.000` (482 records)
  - `Pounds(£)`: `1.300` (80 records)
  - `Brazilian Real(R$)`: `0.180` (60 records)
  - `Emirati Diram(AED)`: `0.270` (60 records)
  - `Rand(R)`: `0.055` (60 records)
  - `NewZealand($)`: `0.600` (40 records)
  - `Turkish Lira(TL)`: `0.029` (34 records)
  - `Botswana Pula(P)`: `0.074` (22 records)
  - `Indonesian Rupiah(IDR)`: `0.000065` (21 records)
  - `Qatari Rial(QR)`: `0.270` (20 records)
  - `Sri Lankan Rupee(LKR)`: `0.00330` (20 records)
- **Validation**: Exchange rates are documented as **fixed benchmark assumptions**, not live FX streams.

---

## 6. Adoption Metrics Audit
- **Online Delivery Adoption Rate**:
  - Numerator: `2,451` restaurants (`has_online_delivery == 1`)
  - Denominator: `9,551` total restaurants
  - Result: `(2,451 / 9,551) * 100 = 25.6622%` -> **`25.66%`**
- **Table Booking Adoption Rate**:
  - Numerator: `1,158` restaurants (`has_table_booking == 1`)
  - Denominator: `9,551` total restaurants
  - Result: `(1,158 / 9,551) * 100 = 12.1243%` -> **`12.12%`**

---

## 7. Revenue Classification Audit
- **Dataset Finding**: The raw dataset contains **no order-level transaction logs or actual corporate ledger entries**.
- **Resolution**: All UI cards, tables, SQL views, and Power BI export documentation explicitly state **"Estimated Monthly Revenue (Proxy)"** to ensure total transparency.

---

## 8. Automated Test Suite Execution
- **Command Executed**: `python -m pytest tests/ -rA`
- **Results**:
  - `test_cleaned_dataset_integrity`: **PASSED**
  - `test_duplicate_restaurant_handling`: **PASSED**
  - `test_currency_conversion`: **PASSED**
  - `test_adoption_percentages_formulas`: **PASSED**
  - `test_estimated_revenue_formula`: **PASSED**
  - `test_database_star_schema`: **PASSED**
  - `test_powerbi_exports_exist`: **PASSED**
  - `test_python_vs_sql_kpi_consistency`: **PASSED**
  - `test_dashboard_payload_consistency`: **PASSED**
- **Total**: **`9 passed in 0.48s`** (100% pass rate).

---

## 9. Dashboard Label Audit
- **Index.html & App.js**:
  - Verified that all static HTML fallbacks and dynamic JS text render mathematically accurate labels.
  - KPI cards updated to:
    - `Total Restaurants (Observed)`
    - `Est. Monthly Revenue (Proxy)`
    - `Avg Global Rating (Observed)`
    - `Online Delivery Adoption (Derived)`
    - `Table Booking Adoption (Derived)`

---

## 10. Remaining Warnings & Operational Disclaimers
1. **Exchange Rate Drift**: FX conversion uses static operational rates. Historical or real-time currency fluctuations are not reflected.
2. **Revenue Proxy Sensitivity**: Estimated revenue is proportional to review vote volume and price point. It should be used for cross-city relative market benchmarking rather than tax/accounting reporting.

---

## 11. Final Audit Determination

**FINAL AUDIT STATUS**:

`DATA VALIDATED`
