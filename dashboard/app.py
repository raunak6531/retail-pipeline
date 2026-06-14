import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os
import google.generativeai as genai

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="🛒",
    layout="wide"
)

DB_PATH = "data/retail.db"

# ── DB HELPER ─────────────────────────────────────────────────────────────────

@st.cache_data
def query(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def get_schema_info() -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    schema = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cursor.fetchall()]
        schema.append(f"Table '{table}': {', '.join(cols)}")
    conn.close()
    return "\n".join(schema)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

st.sidebar.title("🛒 Retail Analytics")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["📊 Overview", "📦 Products", "🗺️ Regional", "🤖 AI Query"])
st.sidebar.markdown("---")
st.sidebar.caption("Data: 50K retail transactions | DB: SQLite")

# ── OVERVIEW PAGE ─────────────────────────────────────────────────────────────

if page == "📊 Overview":
    st.title("📊 Sales Overview")

    # KPI cards
    kpis = query("""
        SELECT
            COUNT(transaction_id)  AS total_orders,
            ROUND(SUM(net_revenue), 0) AS total_revenue,
            ROUND(AVG(net_revenue), 0) AS avg_order_value,
            ROUND(SUM(CASE WHEN is_returned=1 THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) AS return_rate
        FROM sales
    """)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Orders",      f"{int(kpis['total_orders'][0]):,}")
    c2.metric("Net Revenue (₹)",   f"₹{int(kpis['total_revenue'][0]):,}")
    c3.metric("Avg Order Value",   f"₹{int(kpis['avg_order_value'][0]):,}")
    c4.metric("Return Rate",       f"{kpis['return_rate'][0]}%")

    st.markdown("---")

    # Monthly revenue trend
    monthly = query("""
        SELECT year, month, ROUND(SUM(net_revenue),0) AS revenue, COUNT(*) AS orders
        FROM sales WHERE net_revenue > 0
        GROUP BY year, month ORDER BY year, month
    """)
    monthly["period"] = monthly["month"].astype(str).str.zfill(2) + "/" + monthly["year"].astype(str)

    fig = px.line(monthly, x="period", y="revenue",
                  title="Monthly Net Revenue Trend",
                  labels={"revenue": "Revenue (₹)", "period": "Month"},
                  markers=True, color_discrete_sequence=["#FF6B35"])
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # Category split
    cat = query("""
        SELECT category, ROUND(SUM(net_revenue),0) AS revenue
        FROM sales WHERE net_revenue > 0
        GROUP BY category ORDER BY revenue DESC
    """)

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.pie(cat, names="category", values="revenue",
                      title="Revenue by Category",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        pay = query("""
            SELECT payment_method, COUNT(*) AS txns
            FROM sales GROUP BY payment_method ORDER BY txns DESC
        """)
        fig3 = px.bar(pay, x="payment_method", y="txns",
                      title="Transactions by Payment Method",
                      color="txns", color_continuous_scale="Oranges",
                      labels={"txns": "Transactions", "payment_method": "Method"})
        st.plotly_chart(fig3, use_container_width=True)

    # Weekend vs Weekday
    st.markdown("### 📅 Weekday vs Weekend Performance")
    wknd = query("""
        SELECT
            CASE WHEN weekday IN ('Saturday','Sunday') THEN 'Weekend' ELSE 'Weekday' END AS day_type,
            COUNT(*) AS orders, ROUND(SUM(net_revenue),0) AS revenue
        FROM sales WHERE net_revenue > 0
        GROUP BY day_type
    """)
    c1, c2 = st.columns(2)
    fig4 = px.bar(wknd, x="day_type", y="orders", color="day_type",
                  title="Orders: Weekday vs Weekend",
                  color_discrete_sequence=["#4ECDC4", "#FF6B35"])
    c1.plotly_chart(fig4, use_container_width=True)

    fig5 = px.bar(wknd, x="day_type", y="revenue", color="day_type",
                  title="Revenue: Weekday vs Weekend",
                  color_discrete_sequence=["#4ECDC4", "#FF6B35"])
    c2.plotly_chart(fig5, use_container_width=True)


# ── PRODUCTS PAGE ─────────────────────────────────────────────────────────────

elif page == "📦 Products":
    st.title("📦 Product Performance")

    category_filter = st.selectbox("Filter by Category", ["All"] + query(
        "SELECT DISTINCT category FROM sales ORDER BY category"
    )["category"].tolist())

    where = "" if category_filter == "All" else f"WHERE category = '{category_filter}'"

    top_products = query(f"""
        SELECT product_name, category,
               SUM(quantity) AS units_sold,
               ROUND(SUM(net_revenue),0) AS total_revenue,
               ROUND(AVG(discount_pct)*100,1) AS avg_discount
        FROM sales {where} AND net_revenue > 0
        GROUP BY product_name, category
        ORDER BY total_revenue DESC
        LIMIT 15
    """ if where else f"""
        SELECT product_name, category,
               SUM(quantity) AS units_sold,
               ROUND(SUM(net_revenue),0) AS total_revenue,
               ROUND(AVG(discount_pct)*100,1) AS avg_discount
        FROM sales WHERE net_revenue > 0
        GROUP BY product_name, category
        ORDER BY total_revenue DESC
        LIMIT 15
    """)

    fig = px.bar(top_products, x="total_revenue", y="product_name",
                 orientation="h", color="category",
                 title="Top 15 Products by Revenue",
                 labels={"total_revenue": "Revenue (₹)", "product_name": "Product"},
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Discount vs Revenue Relationship")
    scatter = query("""
        SELECT product_name, category,
               ROUND(AVG(discount_pct)*100,1) AS avg_discount,
               ROUND(SUM(net_revenue),0) AS total_revenue,
               SUM(quantity) AS units_sold
        FROM sales WHERE net_revenue > 0
        GROUP BY product_name, category
    """)
    fig2 = px.scatter(scatter, x="avg_discount", y="total_revenue",
                      size="units_sold", color="category", hover_name="product_name",
                      labels={"avg_discount": "Avg Discount (%)", "total_revenue": "Revenue (₹)"},
                      title="Discount % vs Total Revenue (bubble = units sold)")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Revenue Bucket Distribution")
    buckets = query("""
        SELECT revenue_bucket, COUNT(*) AS txns, ROUND(SUM(net_revenue),0) AS revenue
        FROM sales WHERE net_revenue > 0
        GROUP BY revenue_bucket
        ORDER BY revenue DESC
    """)
    st.dataframe(buckets, use_container_width=True)


# ── REGIONAL PAGE ─────────────────────────────────────────────────────────────

elif page == "🗺️ Regional":
    st.title("🗺️ Regional Performance")

    regional = query("""
        SELECT region,
               ROUND(SUM(net_revenue),0) AS total_revenue,
               COUNT(*) AS total_orders,
               ROUND(AVG(net_revenue),0) AS avg_order_value,
               ROUND(SUM(CASE WHEN is_returned=1 THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS return_rate
        FROM sales
        GROUP BY region ORDER BY total_revenue DESC
    """)

    st.dataframe(regional, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(regional, x="region", y="total_revenue", color="region",
                     title="Net Revenue by Region",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(regional, x="region", y="return_rate", color="region",
                      title="Return Rate by Region (%)",
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Category Revenue Heatmap by Region")
    heat_data = query("""
        SELECT region, category, ROUND(SUM(net_revenue),0) AS revenue
        FROM sales WHERE net_revenue > 0
        GROUP BY region, category
    """)
    pivot = heat_data.pivot(index="region", columns="category", values="revenue").fillna(0)
    fig3 = px.imshow(pivot, title="Revenue Heatmap: Region × Category",
                     color_continuous_scale="Oranges",
                     labels={"color": "Revenue (₹)"})
    st.plotly_chart(fig3, use_container_width=True)


# ── AI QUERY PAGE ─────────────────────────────────────────────────────────────

elif page == "🤖 AI Query":
    st.title("🤖 Ask AI About Your Sales Data")
    st.markdown("Ask questions in plain English — the AI will generate and run the SQL for you.")

    api_key = st.text_input("Enter your Gemini API Key", type="password",
                             help="Get a free key at https://aistudio.google.com/")

    question = st.text_area("Your question", placeholder="e.g. Which region had the highest return rate in Q3?")

    if st.button("Ask AI") and question and api_key:
        schema = get_schema_info()
        prompt = f"""You are a data analyst assistant. Given the following SQLite database schema:

{schema}

Generate a single valid SQLite SQL query to answer this question: "{question}"

Rules:
- Return ONLY the SQL query, nothing else
- No markdown formatting, no backticks
- Use only tables and columns that exist in the schema above
- For revenue calculations use net_revenue column
- Keep the query concise and correct
"""
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            generated_sql = response.text.strip()

            st.markdown("**Generated SQL:**")
            st.code(generated_sql, language="sql")

            result_df = query(generated_sql)
            st.markdown("**Result:**")
            st.dataframe(result_df, use_container_width=True)

            if len(result_df.columns) == 2:
                try:
                    fig = px.bar(result_df,
                                 x=result_df.columns[0],
                                 y=result_df.columns[1],
                                 color_discrete_sequence=["#FF6B35"])
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    pass

        except Exception as e:
            st.error(f"Error: {e}")
    elif st.button("Ask AI"):
        st.warning("Please enter both a question and your API key.")
