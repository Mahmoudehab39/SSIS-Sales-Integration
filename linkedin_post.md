Just wrapped up an ETL project using SQL Server Integration Services (SSIS) 🚀

The challenge: 3 distributors, 3 different schemas, 2 file formats (a tab-delimited text file + Excel), and dates in different shapes (`03062019`, `01-06-2019`, real Excel dates).

What I built:
✅ One SSIS package that extracts, cleans and merges everything into a single SQL Server table
✅ Column mapping across schemas, date standardization, type casting and a derived `TotalAmount` metric
✅ A reject path: rows with zero quantity go to a separate table with a reason instead of disappearing
✅ Reconciliation checks: 16,130 source rows = 15,996 loaded + 134 rejected

The most interesting part wasn't the tooling, it was the profiling. Two distributors reported the amount as a *line total* while the third reported a *unit value*. Blindly applying `Qty × Val` would have inflated the numbers and turned returns into positive sales. Checking the data before trusting the formula saved the model.

Key takeaways:
• Profile before you build, validate after you load
• Don't silently delete odd rows (returns, outliers), route and review them
• Document your assumptions

Code and write-up on GitHub: [link]

Next up: a Power BI report on top of the warehouse.

#DataEngineering #SSIS #ETL #SQLServer #DataWarehouse #BusinessIntelligence
