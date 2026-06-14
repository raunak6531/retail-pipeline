# 🛒 Retail Sales Data Pipeline & Analytics Dashboard

An end-to-end **data engineering project** that simulates a real-world retail analytics workflow — from raw data ingestion to an interactive business intelligence dashboard.

Built with Python, SQLite, Pandas, and Streamlit. Includes an AI-powered natural language query interface using the Gemini API.

---

## 📌 What This Project Does

| Stage | What Happens |
|---|---|
| **Generate** | Synthesizes 50,000 realistic retail transactions across 5 categories, 5 regions, and 25 products |
| **Extract** | Reads raw CSV data and validates schema |
| **Transform** | Cleans duplicates, fixes invalid prices, derives time columns, computes net revenue after returns |
| **Load** | Writes clean data + 3 pre-aggregated summary tables into a SQLite database |
| **Analyze** | 8 SQL analytics queries covering revenue trends, regional splits, product performance |
| **Visualize** | Streamlit dashboard with KPI cards, trend charts, heatmaps, and scatter plots |
| **AI Query** | Natural language → SQL → Result, powered by Gemini 2.0 Flash |

---

## 🗂️ Project Structure

```
retail-pipeline/
│
├── pipeline/
│   ├── generate_data.py      # Synthetic data generator (50K records)
│   └── etl.py                # Extract → Transform → Load pipeline
│
├── dashboard/
│   └── app.py                # Streamlit multi-page analytics dashboard
│
├── sql/
│   └── analytics.sql         # 8 hand-written analytics queries
│
├── data/                     # Auto-created on first run
│   ├── raw_sales.csv         # Raw generated data
│   └── retail.db             # SQLite database (fact + summary tables)
│
├── run_pipeline.py           # Single entry point — run this first
└── requirements.txt
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/retail-pipeline.git
cd retail-pipeline
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the ETL pipeline
```bash
python run_pipeline.py
```
This generates the data, runs all transformations, and loads everything into `data/retail.db`.

**Expected output:**
```
Total records processed : 50,000
Total net revenue       : ₹145,594,295.01
Avg order value         : ₹3,063.98
Return rate             : 5.0%
```

### 4. Launch the dashboard
```bash
streamlit run dashboard/app.py
```

---

## 📊 Dashboard Pages

### Overview
- KPI cards: total orders, net revenue, avg order value, return rate
- Monthly revenue trend line chart
- Revenue split by category (pie chart)
- Payment method distribution
- Weekday vs Weekend performance comparison

### Products
- Top 15 products by revenue (filterable by category)
- Discount % vs Revenue scatter plot (bubble = units sold)
- Revenue bucket distribution (Low / Medium / High / Premium)

### Regional
- Performance table: revenue, orders, avg order value, return rate per region
- Regional revenue bar chart
- Revenue heatmap: Region × Category

### AI Query (Gemini-powered)
- Enter any business question in plain English
- AI generates the SQL, runs it against the database, and displays results
- Auto-visualizes 2-column results as bar charts

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **Python** | Core language |
| **Pandas & NumPy** | Data transformation and cleaning |
| **SQLite** | Lightweight relational database |
| **SQL** | Analytics queries and aggregations |
| **Streamlit** | Interactive dashboard frontend |
| **Plotly** | Charts and visualizations |
| **Google Gemini API** | Natural language to SQL conversion |
| **Logging** | Pipeline observability |

---

## 🧩 Key Engineering Decisions

- **Modular ETL**: Extract, Transform, and Load are separate functions — easy to swap the source (CSV → API → cloud storage) without changing the rest.
- **Pre-aggregated summary tables**: Dashboard queries hit lightweight summary tables, not the full 50K-row fact table, keeping the UI fast.
- **Schema-aware AI prompting**: The AI query feature dynamically reads the actual database schema before prompting Gemini — so it stays accurate even if the schema changes.
- **Data quality checks**: The transform step handles duplicates, null dates, zero/negative prices, and out-of-range discounts before anything touches the database.

---

## 📈 Sample Insights from the Data

- **Electronics** and **Home & Kitchen** drive the highest average order values
- **Weekend** transactions account for ~29% of orders but have a slightly higher avg order value
- **Return rate** is consistent (~5%) across all regions — suggesting a product/logistics issue rather than a regional one
- **UPI** is the most common payment method, followed by Credit Card

---

## 🔮 Future Improvements

- [ ] Replace SQLite with PostgreSQL for production-scale use
- [ ] Add incremental loading (only process new records each run)
- [ ] Schedule pipeline runs with Apache Airflow or Prefect
- [ ] Connect to a real data source (e.g. Kaggle retail dataset)
- [ ] Add anomaly detection for unusual spikes in return rate

---

## 📄 License

MIT License — free to use and modify.
