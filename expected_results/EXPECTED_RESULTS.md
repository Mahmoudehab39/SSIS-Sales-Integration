# Expected results (use these to verify your run)

After running the SSIS package, the SQL checks in `sql/03_validation_checks.sql` must return:

| Metric | Expected |
|---|---|
| Source rows (D1 + D2 + D3) | 1,051 + 14,675 + 404 = **16,130** |
| Rows in `dbo.FactSales` | **15,996** |
| Rows in `dbo.RejectedSales` | **134** (D1: 4, D2: 130, D3: 0) |
| `FactSales` + `RejectedSales` | **16,130** |

## Per distributor (`dbo.FactSales`)

| Distributor | Rows | Sum(Qty) | Sum(TotalAmount) | Min date | Max date |
|---|---|---|---|---|---|
| Distributor 1 | 1,047 | 5,925 | 564,811.76250 | 2019-06-01 | 2019-07-01 |
| Distributor 2 | 14,545 | 91,830 | 2,208,545.09430 | 2019-10-07 | 2019-10-07 |
| Distributor 3 | 404 | 38,004 | 556,179.77100 | 2019-06-01 | 2019-06-01 |

## Rule checks
- Item codes not upper-case: **0**
- Rows with `Qty < 0` and `TotalAmount > 0`: **0** (186 return rows are kept with negative totals)

## Files
- `FactSales_expected.csv` – the exact rows expected in `dbo.FactSales` (order may differ)
- `RejectedSales_expected.csv` – the exact rows expected in `dbo.RejectedSales`
- `summary_expected.csv` – the per-distributor table above

## Reproduce without SSIS
```bash
pip install pandas openpyxl
python scripts/verify_expected_results.py sample_data expected_results
```
The script re-implements the same rules in pandas straight from the source files.

## Rules used
- D1: `TotalAmount = Qty × Val` (Val is a unit value). D2 and D3: `TotalAmount = Val` (Sales / Value are already line totals).
- Rows with `Qty = 0` or `Val IS NULL` are rejected.
- Distributor 2 was converted from `.xls` to `.xlsx` before use.
