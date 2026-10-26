"""Independent re-implementation of the SSIS logic in pandas.
Reads the three source files and prints the numbers the SSIS package + SQL checks should produce.
Usage:  python scripts/verify_expected_results.py [path_to_sample_data]
Requires: pandas, openpyxl
"""
import sys
from pathlib import Path
import pandas as pd

base = Path(sys.argv[1] if len(sys.argv) > 1 else "sample_data")

# --- Distributor 1: tab-delimited text, date = ddMMyyyy (leading zero sometimes lost) ---
d1 = pd.read_csv(base / "Distributor1.txt", sep="\t", dtype=str)
d1.columns = [c.strip() for c in d1.columns]
d1["SalesDate"] = pd.to_datetime(d1["Date"].str.strip().str.zfill(8), format="%d%m%Y")
d1["Qty"] = d1["Qty"].astype(int)
d1["Val"] = d1["Val"].str.replace(",", "").astype(float)
d1["ItemCode"] = d1["Item Code"].str.strip().str.upper()
d1["Distributor"] = "Distributor 1"
d1["TotalAmount"] = d1["Qty"] * d1["Val"]            # Val = unit value

# --- Distributor 2: Excel, real dates, Sales = line total ---
d2 = pd.read_excel(base / "Distributor2.xlsx").rename(columns={"QTY": "Qty", "Sales": "Val"})
d2["SalesDate"] = pd.to_datetime(d2["Date"])
d2["ItemCode"] = d2["Item Code"].astype(str).str.strip().str.upper()
d2["Distributor"] = "Distributor 2"
d2["TotalAmount"] = d2["Val"]                         # Val already a line total

# --- Distributor 3: Excel, Value = line total ---
d3 = pd.read_excel(base / "Distributor3.xlsx").rename(columns={"Quantity": "Qty", "Value": "Val"})
d3["SalesDate"] = pd.to_datetime(d3["Date"].astype(str).str.strip(), format="%d-%m-%Y")
d3["ItemCode"] = d3["Item Code"].astype(str).str.strip().str.upper()
d3["Distributor"] = "Distributor 3"
d3["TotalAmount"] = d3["Val"]

cols = ["Distributor", "ItemCode", "SalesDate", "Qty", "Val", "TotalAmount"]
allr = pd.concat([d[cols] for d in (d1, d2, d3)], ignore_index=True)
rejected = allr[(allr.Qty == 0) | allr.Val.isna()]
loaded = allr.drop(rejected.index)

print("Source rows        :", len(allr))
print("Loaded (FactSales) :", len(loaded))
print("Rejected           :", len(rejected))
print()
summary = loaded.groupby("Distributor").agg(
    Rows=("Qty", "size"), Qty=("Qty", "sum"), Total=("TotalAmount", "sum"),
    MinDate=("SalesDate", "min"), MaxDate=("SalesDate", "max"))
summary["Total"] = summary["Total"].round(5)
print(summary)
print()
print("Rejected per distributor:\n", rejected.groupby("Distributor").size())
print("Returns (Qty<0) kept     :", int((loaded.Qty < 0).sum()))
print("Returns with total > 0   :", int(((loaded.Qty < 0) & (loaded.TotalAmount > 0)).sum()))

if len(sys.argv) > 2:  # optional: write expected output files
    out = Path(sys.argv[2]); out.mkdir(exist_ok=True)
    loaded.to_csv(out / "FactSales_expected.csv", index=False, date_format="%Y-%m-%d")
    rejected.to_csv(out / "RejectedSales_expected.csv", index=False, date_format="%Y-%m-%d")
    summary.to_csv(out / "summary_expected.csv")
