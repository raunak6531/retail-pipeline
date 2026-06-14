"""
run_pipeline.py
───────────────
Entry point: generates data, runs ETL, prints a quick summary.
Run this before launching the dashboard.

Usage:
    python run_pipeline.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from pipeline.generate_data import generate_sales_data
from pipeline.etl import run_pipeline


def print_summary(df):
    print("\n" + "=" * 50)
    print("PIPELINE SUMMARY")
    print("=" * 50)
    print(f"  Total records processed : {len(df):,}")
    print(f"  Date range              : {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"  Total net revenue       : ₹{df['net_revenue'].sum():,.2f}")
    print(f"  Avg order value         : ₹{df['net_revenue'][df['net_revenue']>0].mean():,.2f}")
    print(f"  Return rate             : {df['is_returned'].mean()*100:.1f}%")
    print(f"  Categories              : {', '.join(df['category'].unique())}")
    print(f"  Regions                 : {', '.join(df['region'].unique())}")
    print("=" * 50)
    print("\nNext step → launch dashboard:")
    print("  streamlit run dashboard/app.py\n")


if __name__ == "__main__":
    print("\nStep 1/2 — Generating synthetic retail data...")
    generate_sales_data(num_records=50000)

    print("\nStep 2/2 — Running ETL pipeline...")
    clean_df = run_pipeline(
        raw_path="data/raw_sales.csv"
    )

    print_summary(clean_df)
