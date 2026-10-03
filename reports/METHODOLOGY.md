# Food Delivery Analytics & Operations Intelligence - Methodology & Data Dictionary

## 1. Dataset Grain Definition
- **Entity Level**: Restaurant-Level Grain.
- **Exact Row Count**: `9,551` records.
- **Unique Identifier**: `restaurant_id` (Primary Key).
- **Uniqueness Check**: `9,551` unique `restaurant_id`s out of `9,551` rows (`0` duplicates).
- **Important Distinction**: This dataset represents **restaurant profiles and aggregate operational attributes**, NOT order-level transaction logs or individual customer receipts.

---

## 2. Metric Classification Framework

All metrics in the platform are explicitly categorized into one of four classes:

1. **OBSERVED**: Directly captured raw data fields without mathematical transformation.
2. **DERIVED**: Mathematical or categorical calculations based on observed fields.
3. **ESTIMATED**: Derived calculations that incorporate fixed baseline assumptions.
4. **PROXY**: Model-based surrogate metrics representing unobserved metrics (e.g. estimated revenue from votes).

---

## 3. Data Dictionary & Metric Classification Table

| Metric / Column | Data Type | Classification | Source Column(s) | Formula / Definition | Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **restaurant_id** | Integer | OBSERVED | `Restaurant ID` | Raw unique ID | Primary Key identifying restaurant profile |
| **restaurant_name** | String | OBSERVED | `Restaurant Name` | Raw text | Name of restaurant establishment |
| **city** | String | OBSERVED | `City` | Raw text | Geographic city location |
| **country_code** | Integer | OBSERVED | `Country Code` | Raw integer | ISO numerical country code |
| **aggregate_rating** | Float | OBSERVED | `Aggregate rating` | Raw float (0.0 to 5.0) | Average customer rating score |
| **votes** | Integer | OBSERVED | `Votes` | Raw integer | Total count of customer review votes |
| **avg_cost_for_two** | Float | OBSERVED | `Average Cost for two` | Raw float | Average bill amount for two people in local currency |
| **currency** | String | OBSERVED | `Currency` | Raw string | Local currency code/text |
| **has_online_delivery** | Binary (0/1)| OBSERVED | `Has Online delivery` | `1` if Yes else `0` | Flag indicating online food delivery enablement |
| **has_table_booking** | Binary (0/1)| OBSERVED | `Has Table booking` | `1` if Yes else `0` | Flag indicating table reservation service |
| **primary_cuisine** | String | DERIVED | `cuisines` | `cuisines.split(',')[0]` | Dominant cuisine offering |
| **cuisine_count** | Integer | DERIVED | `cuisines` | `len(cuisines.split(','))` | Variety count of cuisines served |
| **delivery_adoption_pct**| Float (%) | DERIVED | `has_online_delivery` | `(SUM(has_online_delivery) / COUNT(*)) * 100` | Percentage of restaurants offering online delivery |
| **booking_adoption_pct** | Float (%) | DERIVED | `has_table_booking` | `(SUM(has_table_booking) / COUNT(*)) * 100` | Percentage of restaurants offering table reservations |
| **avg_cost_for_two_usd** | Float | ESTIMATED | `avg_cost_for_two`, `currency` | `avg_cost_for_two * fx_rate` | Normalized cost for two in USD (Fixed FX rates) |
| **engagement_score** | Float | PROXY | `votes`, `aggregate_rating` | `log1p(votes) * aggregate_rating` | Synthetic customer engagement & popularity index |
| **est_monthly_orders** | Integer | PROXY | `votes`, `has_online_delivery` | `votes * (1.5 if delivery==1 else 1.0)` | Estimated monthly order volume proxy |
| **est_monthly_revenue_usd**| Float | PROXY | `est_monthly_orders`, `avg_cost_for_two_usd` | `est_monthly_orders * (avg_cost_for_two_usd / 2)` | Estimated monthly revenue proxy (NOT actual transactional ledger) |

---

## 4. Currency Conversion Methodology (FX Assumptions)

Exchange rates are applied to convert 12 local currencies into USD for comparative benchmark analysis. These rates represent **fixed operational baseline assumptions** and are **NOT real-time FX rates**:

- `Indian Rupees(Rs.)`: `0.012`
- `Dollar($)`: `1.0`
- `Pounds(£)`: `1.30`
- `Brazilian Real(R$)`: `0.18`
- `Emirati Diram(AED)`: `0.27`
- `Rand(R)`: `0.055`
- `NewZealand($)`: `0.60`
- `Turkish Lira(TL)`: `0.029`
- `Botswana Pula(P)`: `0.074`
- `Indonesian Rupiah(IDR)`: `0.000065`
- `Qatari Rial(QR)`: `0.27`
- `Sri Lankan Rupee(LKR)`: `0.0033`

---

## 5. Revenue Estimation Model Disclaimer

> [!IMPORTANT]
> **No Actual Transactional Revenue Field Exists**:
> The raw dataset does not contain transactional order logs or merchant payment settlement statements.
> The **"Estimated Monthly Revenue (USD)"** metric is a mathematical proxy model intended exclusively for relative performance segmentation across cities and price tiers. It must **never** be cited as actual financial revenue or audited corporate earnings.
