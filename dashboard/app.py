import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from groq import Groq

load_dotenv()

# ── PREMIUM CSS ───────────────────────────────────────────────────────────────

def inject_premium_css():
    st.markdown("""
    <style>
    /* ── Base & Background ── */
    .stApp {
        background-color: #0f172a;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-size: 0.95rem;
        padding: 6px 0;
        color: #94a3b8;
        transition: color 0.2s;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        color: #6366f1;
    }

    /* ── Page header ── */
    .page-header {
        padding: 1.4rem 0 0.6rem 0;
        border-bottom: 2px solid #6366f1;
        margin-bottom: 1.6rem;
    }
    .page-header h1 {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
        letter-spacing: -0.3px;
    }
    .page-header p {
        font-size: 0.85rem;
        color: #64748b;
        margin: 4px 0 0 0;
    }

    /* ── Section label ── */
    .section-label {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #6366f1;
        margin: 1.6rem 0 0.8rem 0;
    }

    /* ── KPI card container ── */
    .kpi-container {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.35);
        margin-bottom: 1.6rem;
    }
    .kpi-container-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.4px;
        text-transform: uppercase;
        color: #475569;
        margin-bottom: 1rem;
    }

    /* ── Streamlit metric widget overrides ── */
    div[data-testid="metric-container"] {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 12px rgba(99,102,241,0.08);
        transition: box-shadow 0.25s, border-color 0.25s;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #6366f1;
        box-shadow: 0 4px 20px rgba(99,102,241,0.22);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        color: #64748b !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f8fafc;
    }

    /* ── Chart card wrapper ── */
    div[data-testid="stPlotlyChart"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 0.5rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
    }

    /* ── Dataframe ── */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #334155;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    }

    /* ── Divider ── */
    hr {
        border: none;
        border-top: 1px solid #1e293b;
        margin: 1.4rem 0;
    }

    /* ── Button ── */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #6366f1, #14b8a6);
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 0.55rem 1.8rem;
        font-weight: 600;
        letter-spacing: 0.4px;
        transition: opacity 0.2s, box-shadow 0.2s;
    }
    div[data-testid="stButton"] > button:hover {
        opacity: 0.88;
        box-shadow: 0 4px 18px rgba(99,102,241,0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="🛒",
    layout="wide"
)

inject_premium_css()

# ── DB ENGINE ─────────────────────────────────────────────────────────────────

engine = create_engine(os.getenv("DATABASE_URL"))

# ── DB HELPER ─────────────────────────────────────────────────────────────────

@st.cache_data
def query(sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, engine)

def get_schema_info() -> str:
    schema_sql = """
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """
    df = pd.read_sql_query(schema_sql, engine)
    schema = []
    for table, group in df.groupby("table_name"):
        cols = ", ".join(group["column_name"].tolist())
        schema.append(f"Table '{table}': {cols}")
    return "\n".join(schema)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

st.sidebar.title("🛒 Retail Analytics")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["📊 Overview", "📦 Products", "🗺️ Regional", "🤖 AI Query"])
st.sidebar.markdown("---")
st.sidebar.caption("Data: 50K retail transactions | DB: PostgreSQL (Supabase)")

# ── OVERVIEW PAGE ─────────────────────────────────────────────────────────────

if page == "📊 Overview":
    st.markdown("""
    <div class="page-header">
        <h1>📊 Sales Overview</h1>
        <p>Full-year 2023 · 50 000 transactions · Supabase PostgreSQL</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI cards ────────────────────────────────────────────────────────────
    kpis = query("""
        SELECT
            COUNT(transaction_id)  AS total_orders,
            ROUND(SUM(net_revenue)::numeric, 0) AS total_revenue,
            ROUND(AVG(net_revenue)::numeric, 0) AS avg_order_value,
            ROUND((SUM(CASE WHEN is_returned=TRUE THEN 1 ELSE 0 END)*100.0/COUNT(*))::numeric, 1) AS return_rate
        FROM sales
    """)

    st.markdown('<div class="kpi-container"><div class="kpi-container-title">Executive Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🛍️ Total Orders",    f"{int(kpis['total_orders'][0]):,}")
    c2.metric("💰 Net Revenue",      f"₹{int(kpis['total_revenue'][0]):,}")
    c3.metric("🧾 Avg Order Value", f"₹{int(kpis['avg_order_value'][0]):,}")
    c4.metric("↩️ Return Rate",     f"{kpis['return_rate'][0]}%")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Monthly revenue trend ─────────────────────────────────────────────────
    st.markdown('<p class="section-label">Revenue Trends</p>', unsafe_allow_html=True)
    monthly = query("""
        SELECT year, month, ROUND(SUM(net_revenue)::numeric,0) AS revenue, COUNT(*) AS orders
        FROM sales WHERE net_revenue > 0
        GROUP BY year, month ORDER BY year, month
    """)
    monthly["period"] = monthly["month"].astype(str).str.zfill(2) + "/" + monthly["year"].astype(str)

    fig = px.line(monthly, x="period", y="revenue",
                  title="Monthly Net Revenue Trend",
                  labels={"revenue": "Revenue (₹)", "period": "Month"},
                  markers=True,
                  template="plotly_dark",
                  color_discrete_sequence=["#6366f1"])
    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#1e293b"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Category & Payment split ──────────────────────────────────────────────
    st.markdown('<p class="section-label">Category & Payment Breakdown</p>', unsafe_allow_html=True)
    cat = query("""
        SELECT category, ROUND(SUM(net_revenue)::numeric,0) AS revenue
        FROM sales WHERE net_revenue > 0
        GROUP BY category ORDER BY revenue DESC
    """)

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.pie(cat, names="category", values="revenue",
                      title="Revenue by Category",
                      template="plotly_dark",
                      color_discrete_sequence=["#6366f1", "#14b8a6", "#f59e0b", "#ef4444", "#8b5cf6"])
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color="#94a3b8"))
        )
        fig2.update_traces(hole=0.45)   # donut style
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        pay = query("""
            SELECT payment_method, COUNT(*) AS txns
            FROM sales GROUP BY payment_method ORDER BY txns DESC
        """)
        fig3 = px.bar(pay, x="payment_method", y="txns",
                      title="Transactions by Payment Method",
                      template="plotly_dark",
                      color="payment_method",
                      color_discrete_sequence=["#6366f1", "#14b8a6", "#f59e0b", "#ef4444", "#8b5cf6"],
                      labels={"txns": "Transactions", "payment_method": "Method"})
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#1e293b"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── Weekday vs Weekend ────────────────────────────────────────────────────
    st.markdown('<p class="section-label">📅 Weekday vs Weekend Performance</p>', unsafe_allow_html=True)
    wknd = query("""
        SELECT
            CASE WHEN weekday IN ('Saturday','Sunday') THEN 'Weekend' ELSE 'Weekday' END AS day_type,
            COUNT(*) AS orders, ROUND(SUM(net_revenue)::numeric,0) AS revenue
        FROM sales WHERE net_revenue > 0
        GROUP BY day_type
    """)
    c1, c2 = st.columns(2)
    fig4 = px.bar(wknd, x="day_type", y="orders", color="day_type",
                  title="Orders: Weekday vs Weekend",
                  template="plotly_dark",
                  color_discrete_sequence=["#6366f1", "#14b8a6"])
    fig4.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#1e293b"),
    )
    c1.plotly_chart(fig4, use_container_width=True)

    fig5 = px.bar(wknd, x="day_type", y="revenue", color="day_type",
                  title="Revenue: Weekday vs Weekend",
                  template="plotly_dark",
                  color_discrete_sequence=["#6366f1", "#14b8a6"])
    fig5.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#1e293b"),
    )
    c2.plotly_chart(fig5, use_container_width=True)


# ── PRODUCTS PAGE ─────────────────────────────────────────────────────────────

elif page == "📦 Products":
    st.markdown("""
    <div class="page-header">
        <h1>📦 Product Performance</h1>
        <p>Top products, discount impact, and revenue buckets</p>
    </div>
    """, unsafe_allow_html=True)

    category_filter = st.selectbox("Filter by Category", ["All"] + query(
        "SELECT DISTINCT category FROM sales ORDER BY category"
    )["category"].tolist())

    where = "" if category_filter == "All" else f"WHERE category = '{category_filter}'"

    top_products = query(f"""
        SELECT product_name, category,
               SUM(quantity) AS units_sold,
               ROUND(SUM(net_revenue)::numeric,0) AS total_revenue,
               ROUND((AVG(discount_pct)*100)::numeric,1) AS avg_discount
        FROM sales {where} AND net_revenue > 0
        GROUP BY product_name, category
        ORDER BY total_revenue DESC
        LIMIT 15
    """ if where else f"""
        SELECT product_name, category,
               SUM(quantity) AS units_sold,
               ROUND(SUM(net_revenue)::numeric,0) AS total_revenue,
               ROUND((AVG(discount_pct)*100)::numeric,1) AS avg_discount
        FROM sales WHERE net_revenue > 0
        GROUP BY product_name, category
        ORDER BY total_revenue DESC
        LIMIT 15
    """)

    fig = px.bar(top_products, x="total_revenue", y="product_name",
                 orientation="h", color="category",
                 title="Top 15 Products by Revenue",
                 labels={"total_revenue": "Revenue (₹)", "product_name": "Product"},
                 template="plotly_dark",
                 color_discrete_sequence=["#6366f1", "#14b8a6", "#f59e0b", "#ef4444", "#8b5cf6"])
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#1e293b", title="Revenue (₹)"),
        yaxis_title=None
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-label">Discount vs Revenue Relationship</p>', unsafe_allow_html=True)
    scatter = query("""
        SELECT product_name, category,
               ROUND((AVG(discount_pct)*100)::numeric,1) AS avg_discount,
               ROUND(SUM(net_revenue)::numeric,0) AS total_revenue,
               SUM(quantity) AS units_sold
        FROM sales WHERE net_revenue > 0
        GROUP BY product_name, category
    """)
    fig2 = px.scatter(scatter, x="avg_discount", y="total_revenue",
                      size="units_sold", color="category", hover_name="product_name",
                      labels={"avg_discount": "Avg Discount (%)", "total_revenue": "Revenue (₹)"},
                      title="Discount % vs Total Revenue (bubble = units sold)",
                      template="plotly_dark",
                      color_discrete_sequence=["#6366f1", "#14b8a6", "#f59e0b", "#ef4444", "#8b5cf6"])
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#1e293b"),
        yaxis=dict(gridcolor="#1e293b")
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-label">Revenue Bucket Distribution</p>', unsafe_allow_html=True)
    buckets = query("""
        SELECT revenue_bucket, COUNT(*) AS txns, ROUND(SUM(net_revenue)::numeric,0) AS revenue
        FROM sales WHERE net_revenue > 0
        GROUP BY revenue_bucket
        ORDER BY revenue DESC
    """)
    st.dataframe(buckets, use_container_width=True)


# ── REGIONAL PAGE ─────────────────────────────────────────────────────────────

elif page == "🗺️ Regional":
    st.markdown("""
    <div class="page-header">
        <h1>🗺️ Regional Performance</h1>
        <p>Revenue distribution and return rates by geography</p>
    </div>
    """, unsafe_allow_html=True)

    regional = query("""
        SELECT region,
               ROUND(SUM(net_revenue)::numeric,0) AS total_revenue,
               COUNT(*) AS total_orders,
               ROUND(AVG(net_revenue)::numeric,0) AS avg_order_value,
               ROUND((SUM(CASE WHEN is_returned=TRUE THEN 1 ELSE 0 END)*100.0/COUNT(*))::numeric,1) AS return_rate
        FROM sales
        GROUP BY region ORDER BY total_revenue DESC
    """)

    st.dataframe(regional, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(regional, x="region", y="total_revenue", color="region",
                     title="Net Revenue by Region",
                     template="plotly_dark",
                     color_discrete_sequence=["#6366f1", "#14b8a6", "#f59e0b", "#ef4444", "#8b5cf6"])
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            yaxis=dict(gridcolor="#1e293b"),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(regional, x="region", y="return_rate", color="region",
                      title="Return Rate by Region (%)",
                      template="plotly_dark",
                      color_discrete_sequence=["#6366f1", "#14b8a6", "#f59e0b", "#ef4444", "#8b5cf6"])
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            yaxis=dict(gridcolor="#1e293b"),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-label">Category Revenue Heatmap by Region</p>', unsafe_allow_html=True)
    heat_data = query("""
        SELECT region, category, ROUND(SUM(net_revenue)::numeric,0) AS revenue
        FROM sales WHERE net_revenue > 0
        GROUP BY region, category
    """)
    pivot = heat_data.pivot(index="region", columns="category", values="revenue").fillna(0)
    fig3 = px.imshow(pivot, title="Revenue Heatmap: Region × Category",
                     color_continuous_scale="Purples",
                     labels={"color": "Revenue (₹)"},
                     template="plotly_dark")
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig3, use_container_width=True)


# ── AI QUERY PAGE ─────────────────────────────────────────────────────────────

elif page == "🤖 AI Query":
    st.markdown("""
    <div class="page-header">
        <h1>🤖 Ask AI About Your Sales Data</h1>
        <p>Ask questions in plain English — the AI will generate and run the SQL for you.</p>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_area("Your question", placeholder="e.g. Which region had the highest return rate in Q3?")

    ask_clicked = st.button("Ask AI")

    if ask_clicked and question:
        schema = get_schema_info()
        system_prompt = f"""You are a data analyst assistant. Given the following PostgreSQL database schema:

{schema}

Generate a single valid PostgreSQL SQL query to answer the user's question.

Rules:
- Return ONLY the raw SQL query, nothing else
- No markdown formatting, no backticks, no code fences
- Use only tables and columns that exist in the schema above
- For revenue calculations use the net_revenue column
- Keep the query concise and correct
"""
        try:
            groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": question},
                ],
            )
            generated_sql = completion.choices[0].message.content.strip()

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
                                 template="plotly_dark",
                                 color_discrete_sequence=["#6366f1"])
                    fig.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        yaxis=dict(gridcolor="#1e293b"),
                        xaxis=dict(showgrid=False)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    pass

        except Exception as e:
            st.error(f"Error: {e}")
    elif ask_clicked:
        st.warning("Please enter a question first.")


