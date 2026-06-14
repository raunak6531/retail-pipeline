import pandas as pd
import numpy as np
import sqlite3
import os
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


# ── EXTRACT ──────────────────────────────────────────────────────────────────

def extract(filepath: str) -> pd.DataFrame:
    log.info(f"Extracting data from {filepath}")
    df = pd.read_csv(filepath)
    log.info(f"Loaded {len(df):,} raw records with {df.shape[1]} columns")
    return df


# ── TRANSFORM ─────────────────────────────────────────────────────────────────

def transform(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Starting transformation...")

    original_count = len(df)

    # 1. Drop exact duplicates
    df = df.drop_duplicates(subset=["transaction_id"])
    log.info(f"Removed {original_count - len(df)} duplicate records")

    # 2. Parse and validate dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    invalid_dates = df["date"].isna().sum()
    if invalid_dates:
        log.warning(f"Dropping {invalid_dates} records with unparseable dates")
        df = df.dropna(subset=["date"])

    # 3. Derive time-based columns
    df["year"]    = df["date"].dt.year
    df["month"]   = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["weekday"] = df["date"].dt.day_name()

    # 4. Fix negative or zero prices
    invalid_prices = (df["unit_price"] <= 0) | (df["final_amount"] < 0)
    if invalid_prices.sum():
        log.warning(f"Dropping {invalid_prices.sum()} records with invalid prices")
        df = df[~invalid_prices]

    # 5. Clip discount to valid range [0, 1]
    df["discount_pct"] = df["discount_pct"].clip(0, 1)

    # 6. Recalculate revenue excluding returns
    df["net_revenue"] = np.where(
        df["is_returned"],
        0.0,
        df["final_amount"]
    )

    # 7. Normalize text columns
    df["category"] = df["category"].str.strip().str.title()
    df["region"]   = df["region"].str.strip().str.title()

    # 8. Add revenue bucket for segmentation
    df["revenue_bucket"] = pd.cut(
        df["final_amount"],
        bins=[0, 500, 1500, 5000, float("inf")],
        labels=["Low", "Medium", "High", "Premium"]
    ).astype(str)

    log.info(f"Transformation complete. {len(df):,} clean records ready.")
    return df


# ── LOAD ──────────────────────────────────────────────────────────────────────

def load(df: pd.DataFrame, db_path: str = "data/retail.db"):
    log.info(f"Loading data into SQLite database at {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)

    # Main fact table
    df.to_sql("sales", conn, if_exists="replace", index=False)
    log.info(f"Wrote {len(df):,} rows to 'sales' table")

    # Pre-aggregate summary tables for faster dashboard queries
    _create_summary_tables(conn, df)

    conn.close()
    log.info("Database connection closed. ETL complete.")


def _create_summary_tables(conn: sqlite3.Connection, df: pd.DataFrame):
    # Monthly revenue by category
    monthly = (
        df[df["net_revenue"] > 0]
        .groupby(["year", "month", "category"])
        .agg(total_revenue=("net_revenue", "sum"),
             total_orders=("transaction_id", "count"),
             avg_order_value=("net_revenue", "mean"))
        .reset_index()
    )
    monthly.to_sql("monthly_category_summary", conn, if_exists="replace", index=False)

    # Regional performance
    regional = (
        df[df["net_revenue"] > 0]
        .groupby("region")
        .agg(total_revenue=("net_revenue", "sum"),
             total_orders=("transaction_id", "count"),
             return_rate=("is_returned", "mean"))
        .reset_index()
    )
    regional.to_sql("regional_summary", conn, if_exists="replace", index=False)

    # Top products
    products = (
        df[df["net_revenue"] > 0]
        .groupby(["product_name", "category"])
        .agg(total_revenue=("net_revenue", "sum"),
             units_sold=("quantity", "sum"),
             avg_discount=("discount_pct", "mean"))
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    products.to_sql("product_summary", conn, if_exists="replace", index=False)

    log.info("Created 3 summary tables: monthly_category_summary, regional_summary, product_summary")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def run_pipeline(raw_path: str = "data/raw_sales.csv", db_path: str = "data/retail.db"):
    log.info("=" * 50)
    log.info("RETAIL SALES ETL PIPELINE — START")
    log.info("=" * 50)

    raw_df    = extract(raw_path)
    clean_df  = transform(raw_df)
    load(clean_df, db_path)

    log.info("=" * 50)
    log.info("PIPELINE FINISHED SUCCESSFULLY")
    log.info("=" * 50)
    return clean_df


if __name__ == "__main__":
    run_pipeline()
