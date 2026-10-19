"""Reproducible order-level analysis of the supplied XLSB workbook.

Usage:
    pip install pandas pyxlsb
    python python/analyze_amazon.py
Optional: python python/analyze_amazon.py --sheet 0

Column aliases cover common Amazon sales-report schemas. The script prints
the available columns and exits with a clear message if required fields differ.
"""
from pathlib import Path
import argparse
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/Amazon Sale Report.xlsb"
OUT = ROOT / "analysis"
ALIASES = {
    "order_id": ["order id", "order_id", "order-id", "orderid"],
    "date": ["date", "order date", "order_date"],
    "status": ["status", "order status", "order_status"],
    "amount": ["amount", "sales", "sales amount", "total", "revenue"],
    "category": ["category", "product category", "product_category"],
    "fulfilment": ["fulfilment", "fulfillment", "fulfilled-by", "fulfilled by"],
    "sku": ["sku", "product", "product name", "asin"],
}
def normalize(name):
    return " ".join(str(name).lower().replace("_", " ").replace("-", " ").split())
def pick(columns, aliases):
    mapping = {normalize(c): c for c in columns}
    for alias in aliases:
        if normalize(alias) in mapping:
            return mapping[normalize(alias)]
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheet", default="0", help="Sheet name or zero-based index")
    args = parser.parse_args()
    sheet = int(args.sheet) if args.sheet.isdigit() else args.sheet
    df = pd.read_excel(SOURCE, sheet_name=sheet, engine="pyxlsb")
    cols = {key: pick(df.columns, aliases) for key, aliases in ALIASES.items()}
    print("Workbook columns:", list(df.columns))
    print("Mapped columns:", cols)
    if not cols["order_id"] or not cols["status"]:
        raise SystemExit("Order ID and Status columns are required. Adjust ALIASES to match the workbook.")
    OUT.mkdir(exist_ok=True)
    clean = pd.DataFrame()
    for key, original in cols.items():
        if original:
            clean[key] = df[original]
    clean["order_id"] = clean["order_id"].astype("string").str.strip()
    clean["status"] = clean["status"].astype("string").str.strip()
    clean = clean.dropna(subset=["order_id", "status"])
    if "amount" in clean:
        clean["amount"] = pd.to_numeric(clean["amount"], errors="coerce")
    if "date" in clean:
        # XLSB engines may return Excel serial dates.
        dates = pd.to_datetime(clean["date"], errors="coerce")
        if pd.api.types.is_numeric_dtype(clean["date"]):
            dates = pd.to_datetime(clean["date"], unit="D", origin="1899-12-30", errors="coerce")
        clean["date"] = dates
    clean.to_csv(OUT / "orders_clean.csv", index=False)
    statuses = clean.groupby("status", dropna=False).agg(
        records=("order_id", "size"), distinct_orders=("order_id", "nunique")
    )
    if "amount" in clean:
        statuses["reported_amount"] = clean.groupby("status")["amount"].sum(min_count=1)
    statuses.to_csv(OUT / "status_summary.csv")
    for field in ("category", "fulfilment"):
        if field in clean:
            summary = clean.groupby(field, dropna=False).agg(records=("order_id", "size"))
            if "amount" in clean:
                summary["reported_amount"] = clean.groupby(field)["amount"].sum(min_count=1)
            summary.to_csv(OUT / f"{field}_summary.csv")
    with sqlite3.connect(OUT / "amazon_orders.sqlite") as db:
        clean.to_sql("orders", db, if_exists="replace", index=False)
    print(f"Saved {len(clean):,} records. Distinct orders: {clean.order_id.nunique():,}.")
    print("Note: Row counts and unique orders differ if an order has multiple lines.")
    print("Reported amounts are not automatically net revenue; returns/cancellations need business rules.")

if __name__ == "__main__":
    main()
