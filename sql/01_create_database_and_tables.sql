-- 01_create_database_and_tables.sql
CREATE DATABASE SalesDW;
GO
USE SalesDW;
GO

CREATE TABLE dbo.FactSales (
    SalesID      INT IDENTITY(1,1) PRIMARY KEY,
    Distributor  VARCHAR(20)   NOT NULL,
    ItemCode     VARCHAR(30)   NOT NULL,
    SalesDate    DATE          NOT NULL,
    Qty          INT           NOT NULL,
    Val          DECIMAL(18,5) NOT NULL,
    TotalAmount  DECIMAL(24,5) NOT NULL
);
GO

CREATE TABLE dbo.RejectedSales (
    Distributor  VARCHAR(20),
    ItemCode     VARCHAR(30),
    SalesDate    DATE,
    Qty          INT,
    Val          DECIMAL(18,5),
    RejectReason VARCHAR(100)
);
GO
