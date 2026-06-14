<div align="center">

# 🛒 Retail Analytics Pipeline

**A production-grade data pipeline that generates, cleans, and stores 50 000 synthetic retail transactions in Supabase PostgreSQL — with a Streamlit dashboard powered by Groq AI for natural-language SQL queries.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![PostgreSQL](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-F55036?style=for-the-badge&logo=meta&logoColor=white)](https://groq.com)
[![Plotly](https://img.shields.io/badge/Plotly-Charts-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)

</div>

---

## ✨ What This Project Does

| Stage | What happens |
|---|---|
| **Generate** | Synthesises 50 000 realistic retail transactions across 5 categories, 5 regions, and 5 payment methods for the full year 2023 |
| **Extract** | Reads the raw CSV with Pandas |
| **Transform** | Deduplicates, validates dates & prices, derives time columns, clips discounts, computes `net_revenue`, segments into revenue buckets |
| **Load** | Pushes the cleaned fact table + 3 pre-aggregated summary tables to a **Supabase PostgreSQL** database via SQLAlchemy |
| **Visualise** | A 4-page **Streamlit** dashboard with interactive Plotly charts |
| **Ask AI** | Type a plain-English question → **Groq LLaMA 3.1** generates the SQL → result + chart rendered instantly |

---

## 🗂️ Project Structure

```
retail-pipeline/
│
├── pipeline/
│   ├── generate_data.py   # Synthetic data generator (seeded, reproducible)
│   └── etl.py             # Extract → Transform → Load to PostgreSQL
│
├── dashboard/
│   └── app.py             # 4-page Streamlit dashboard + Groq AI query
│
├── sql/
│   └── analytics.sql      # Reference SQL queries for direct DB exploration
│
├── run_pipeline.py        # Single entry-point: generate → ETL → summary
├── requirements.txt       # Pinned dependencies
└── .env                   # Secrets (DATABASE_URL, GROQ_API_KEY) — never commit
```

---

## 📊 Dashboard Pages

### 📊 Overview
- **KPI cards** — Total Orders · Net Revenue · Avg Order Value · Return Rate
- **Monthly Revenue Trend** — line chart across all 12 months
- **Revenue by Category** — donut chart
- **Transactions by Payment Method** — bar chart
- **Weekday vs Weekend** — side-by-side order & revenue bars

### 📦 Products
- **Top 15 Products by Revenue** — horizontal bar, filterable by category
- **Discount % vs Revenue** — bubble scatter (size = units sold)
- **Revenue Bucket Distribution** — Low / Medium / High / Premium breakdown

### 🗺️ Regional
- **Regional summary table** — revenue, orders, avg order value, return rate per region
- **Net Revenue by Region** — bar chart
- **Return Rate by Region** — bar chart
- **Category × Region Revenue Heatmap** — colour-coded grid

### 🤖 AI Query
- Type any plain-English question about the data
- Groq `llama-3.1-8b-instant` generates a valid PostgreSQL query
- SQL is displayed, executed live, and results rendered as a table + chart

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Data wrangling | Pandas 2.2 · NumPy 1.26 |
| Database ORM | SQLAlchemy 2.0 |
| Database driver | psycopg2-binary |
| Cloud database | Supabase (PostgreSQL) |
| Dashboard | Streamlit 1.35 |
| Charts | Plotly 5.22 |
| AI / LLM | Groq API · LLaMA 3.1 8B Instant |
| Config | python-dotenv |

---

## 🚀 Quick Start

### 1 — Clone & install dependencies

```bash
git clone https://github.com/your-username/retail-pipeline.git
cd retail-pipeline
python -m pip install -r requirements.txt
```

### 2 — Create your `.env` file

```env
DATABASE_URL=postgresql://postgres:<password>@<host>:<port>/<database>
GROQ_API_KEY=gsk_...
```

> **Supabase tip:** Copy the connection string from  
> *Supabase Dashboard → Project → Settings → Database → Connection string → URI*
>
> **Groq API key:** Get a free key at [console.groq.com](https://console.groq.com)

### 3 — Generate data & run the ETL

```bash
python run_pipeline.py
```

This will:
1. Generate `data/raw_sales.csv` with 50 000 records
2. Run the full ETL and push 4 tables to your Supabase database
3. Print a pipeline summary to the terminal

```
==================================================
PIPELINE SUMMARY
==================================================
  Total records processed : 50,000
  Date range              : 2023-01-01 → 2023-12-31
  Total net revenue       : ₹145,594,295.01
  Avg order value         : ₹3,063.98
  Return rate             : 5.0%
  Categories              : Electronics, Sports, Clothing, Home & Kitchen, Grocery
  Regions                 : Central, South, North, East, West
==================================================
```

### 4 — Launch the dashboard

```bash
streamlit run dashboard/app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🗃️ Database Schema

After the ETL runs, four tables exist in the `public` schema:

### `sales` — main fact table (50 000 rows)

| Column | Type | Description |
|---|---|---|
| `transaction_id` | text | Unique ID e.g. `TXN100000` |
| `date` | timestamp | Sale date |
| `product_name` | text | Product name |
| `category` | text | Electronics / Clothing / Grocery / Home & Kitchen / Sports |
| `region` | text | North / South / East / West / Central |
| `quantity` | integer | Units purchased (1–5) |
| `unit_price` | float | Price per unit (₹) |
| `discount_pct` | float | Discount applied (0–0.25) |
| `final_amount` | float | Gross amount after discount |
| `payment_method` | text | Credit Card / UPI / Cash / Debit Card / Net Banking |
| `is_returned` | boolean | Whether the order was returned (~5%) |
| `year` | integer | Derived from date |
| `month` | integer | Derived from date |
| `quarter` | integer | Derived from date |
| `weekday` | text | Day name e.g. `Monday` |
| `net_revenue` | float | `final_amount` if not returned, else `0` |
| `revenue_bucket` | text | Low / Medium / High / Premium |

### `monthly_category_summary`
Pre-aggregated monthly revenue, order count, and avg order value per category.

### `regional_summary`
Pre-aggregated total revenue, orders, and return rate per region.

### `product_summary`
Pre-aggregated revenue, units sold, and avg discount per product.

---

## 🔍 Standalone SQL Queries

`sql/analytics.sql` contains 8 ready-to-run analytical queries:

1. Revenue, orders & return rate overview
2. Monthly revenue trend
3. Top 5 categories by net revenue
4. Regional performance comparison
5. Top 10 products by units sold
6. Payment method distribution
7. Weekend vs weekday sales
8. Revenue bucket segmentation

---

## 🤖 AI Query Examples

Try these in the **🤖 AI Query** tab:

- *"Which region had the highest return rate?"*
- *"What are the top 3 products by revenue in the Electronics category?"*
- *"Show me monthly revenue for Q3 2023."*
- *"Which payment method is most popular on weekends?"*
- *"What percentage of orders fall in the Premium revenue bucket?"*

---

## 🛡️ Environment & Security

- **Never commit `.env`** — it is listed in `.gitignore`
- Rotate your Groq API key periodically at [console.groq.com](https://console.groq.com)
- For production Supabase, enable Row Level Security (RLS) on your tables

---

## 📄 License

MIT © 2024 — free to use, modify, and distribute.
