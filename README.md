# SSIS Sales Data Integration & Consolidation

An ETL project built with **SQL Server Integration Services (SSIS)** that consolidates sales
transactions from three distributors (one flat file, two Excel files, three different schemas)
into a single, standardized **SQL Server data warehouse table**.

## Business problem
Sales and analytics teams received data from three distributors, each with a different file format,
column names and date format, which made consolidated reporting a manual task. The goal: one trusted
table, built automatically.

## Architecture
```
Distributor1.txt (Flat File) ─► Derived Column (clean) ─► Derived Column (TotalAmount) ─┐
Distributor2.xlsx (Excel)    ─► Derived Column (clean) ─► Derived Column (TotalAmount) ─┼─► Union All ─► Conditional Split ─┬─► dbo.FactSales
Distributor3.xlsx (Excel)    ─► Derived Column (clean) ─► Derived Column (TotalAmount) ─┘                                   └─► dbo.RejectedSales
![Data Flow](docs/dataflow.png)
![Validation](docs/validation_results.png)
```

## Source schemas
| Distributor | Format | Columns |
|---|---|---|
| 1 | Tab-delimited text | Customer Code, Item Code, Date, Qty, Val |
| 2 | Excel (.xls) | Date, Item Code, Item Name, Product Line, Client Code, Client Name, Region, QTY, Sales |
| 3 | Excel (.xlsx) | Client Code, Item Code, Item Name, Sales Type, Date, Quantity, Value |

## Target table: `dbo.FactSales`
`SalesID` (identity), `Distributor`, `ItemCode`, `SalesDate`, `Qty`, `Val`, `TotalAmount`
(`Distributor` was added to keep lineage / traceability; the other columns follow the requirement.)

## Transformations
- **Column mapping:** `Qty / QTY / Quantity → Qty`, `Val / Sales / Value → Val`.
- **Dates unified to `DATE`:**
  - D1: text `ddMMyyyy` with no separators (leading zero lost on some rows, e.g. `8062019`) – padded and parsed.
  - D2: native Excel dates.
  - D3: text `dd-MM-yyyy` / Excel date.
- **Cleansing:** item codes trimmed and upper-cased (`rr1572` vs `RR1572`), thousands separators removed from `Val` (`14,400.00`), explicit casts for every type.
- **Validation:** rows with `Qty = 0` or `Val IS NULL` are routed to `dbo.RejectedSales` with a reason instead of being dropped silently.
- **Derived metric:** `TotalAmount`.

## Key data findings & design decisions
- **`Val` means different things per distributor.** Profiling showed `Sales/QTY` is constant per item in D2 (and almost constant in D3), i.e. those columns are *line totals*. In D1, `Val` takes a small set of price-like values unrelated to quantity, i.e. a *unit value*.
  - D1: `TotalAmount = Qty × Val`
  - D2, D3: `TotalAmount = Val` (applying `Qty × Val` would multiply an existing total by quantity again and flip the sign of returns).
- **Returns are kept.** Negative quantities (186 rows) are legitimate returns and reduce sales; they are not deleted.
- **Outliers are not deleted.** Very large quantities (e.g. `-3000`) stay in the warehouse and are reviewed with SQL (see `sql/03_validation_checks.sql`).
- **Known limitations:** D2 contains a single date (2019-10-07); item codes are not comparable across distributors (the three code sets share no values and no mapping table was provided, so an item is identified by `(Distributor, ItemCode)`); the meaning of `Sales Type` in D3 is unknown.

## Validation results
| Check | Result |
|---|---|
| Source rows | 1,051 + 14,675 + 404 = **16,130** |
| Loaded to `FactSales` | **15,996** (D1 1,047 · D2 14,545 · D3 404) |
| Rejected | **134** (D1 4 · D2 130) |
| Loaded + rejected = source | ✔ |
| `TotalAmount` D1 / D2 / D3 | 564,811.76 / 2,208,545.09 / 556,179.77 – matches independent calculation |
| Non-upper-case item codes | 0 |
| Returns with positive total | 0 |

## How to run
1. Run `sql/01_create_database_and_tables.sql` on SQL Server.
2. Open the SSIS project in Visual Studio (SSDT + SSIS extension), point the connection managers to your local source files and to `SalesDW`.
3. Run the package (`sql/02_truncate_before_load.sql` runs first so it is re-runnable).
4. Run `sql/03_validation_checks.sql` and compare with the table above.

## Verify your run
See [`expected_results/EXPECTED_RESULTS.md`](expected_results/EXPECTED_RESULTS.md). You can also reproduce every number without SSIS with `scripts/verify_expected_results.py`.

## Repository structure
```
.
├── README.md
├── ssis/            # SSIS project (.sln, .dtsx, .conmgr)
├── sql/             # table creation, truncate, validation scripts
├── docs/            # requirements PDF, screenshots of the data flow
├── sample_data/     # the three source files (D2 saved as .xlsx)
├── expected_results/# numbers + expected output rows to verify a run
└── scripts/         # pandas re-implementation to reproduce the expected numbers
```

## Tech
SQL Server · SSIS · T-SQL · Excel / flat-file sources

## Next steps
- Power BI report on top of `FactSales` (date table, distributor comparison, returns analysis).
- Item/customer dimensions once a code-mapping table is available.
