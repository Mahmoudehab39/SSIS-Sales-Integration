-- 03_validation_checks.sql  (run after each load)
USE SalesDW;

-- 1) Rows / qty / total per distributor
SELECT Distributor, COUNT(*) AS Rows, SUM(Qty) AS Qty, SUM(TotalAmount) AS Total
FROM dbo.FactSales GROUP BY Distributor;

-- 2) Rejected rows per distributor
SELECT Distributor, COUNT(*) AS Rejected FROM dbo.RejectedSales GROUP BY Distributor;

-- 3) Reconciliation: loaded + rejected must equal source rows (16,130)
SELECT (SELECT COUNT(*) FROM dbo.FactSales) + (SELECT COUNT(*) FROM dbo.RejectedSales) AS TotalRows;

-- 4) Date range per distributor
SELECT Distributor, MIN(SalesDate) AS MinDate, MAX(SalesDate) AS MaxDate
FROM dbo.FactSales GROUP BY Distributor;

-- 5) Item codes must be upper-case (expected 0)
SELECT COUNT(*) FROM dbo.FactSales WHERE ItemCode COLLATE Latin1_General_BIN <> UPPER(ItemCode);

-- 6) Returns must not produce positive totals (expected 0)
SELECT COUNT(*) FROM dbo.FactSales WHERE Qty < 0 AND TotalAmount > 0;

-- 7) Outlier review: largest absolute amounts
SELECT TOP 20 * FROM dbo.FactSales ORDER BY ABS(TotalAmount) DESC;
