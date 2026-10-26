-- 02_truncate_before_load.sql
-- Executed by an Execute SQL Task before the Data Flow so the package is re-runnable.
TRUNCATE TABLE dbo.FactSales;
TRUNCATE TABLE dbo.RejectedSales;
