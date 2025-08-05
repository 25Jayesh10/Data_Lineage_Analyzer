
-- Sample data for Employees with Currency
INSERT INTO AcmeERP.Employees (FirstName, LastName, Department, Position, HireDate, BaseSalary, Currency)
SELECT 
    CONCAT('First', n) AS FirstName,
    CONCAT('Last', n) AS LastName,
    CASE WHEN n % 3 = 0 THEN 'Finance' WHEN n % 3 = 1 THEN 'HR' ELSE 'IT' END AS Department,
    CASE WHEN n % 2 = 0 THEN 'Analyst' ELSE 'Manager' END AS Position,
    DATEADD(DAY, -n * 30, GETDATE()) AS HireDate,
    30000 + (n * 50) AS BaseSalary,
    CASE 
        WHEN n % 4 = 0 THEN 'EUR'
        WHEN n % 4 = 1 THEN 'GBP'
        WHEN n % 4 = 2 THEN 'JPY'
        ELSE 'USD'
    END AS Currency
FROM (SELECT TOP 1000 ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n FROM sys.all_objects) AS numbers;


-- Sample Products
INSERT INTO AcmeERP.Products (ProductName, Category, CostMethod, CurrentStock)
SELECT 
    CONCAT('Product-', n),
    CASE WHEN n % 3 = 0 THEN 'Electronics' WHEN n % 3 = 1 THEN 'Stationery' ELSE 'Office Supplies' END,
    CASE WHEN n % 2 = 0 THEN 'FIFO' ELSE 'LIFO' END,
    50 + (n % 25)
FROM (SELECT TOP 500 ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n FROM sys.all_objects) AS numbers;

-- Sample StockMovements
INSERT INTO AcmeERP.StockMovements (ProductID, MovementDate, Quantity, UnitCost, Direction)
SELECT 
    (n % 500) + 1,
    DATEADD(DAY, -n, GETDATE()),
    (n % 20) + 1,
    10.00 + (n % 5),
    CASE WHEN n % 2 = 0 THEN 'IN' ELSE 'OUT' END
FROM (SELECT TOP 2000 ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n FROM sys.all_objects) AS numbers;

-- Sample Currencies
INSERT INTO AcmeERP.Currencies (CurrencyCode, CurrencyName)
VALUES 
('USD', 'US Dollar'),
('EUR', 'Euro'),
('INR', 'Indian Rupee'),
('GBP', 'British Pound'),
('JPY', 'Japanese Yen');

-- Sample Exchange Rates
INSERT INTO AcmeERP.ExchangeRates (CurrencyCode, RateDate, RateToBase)
SELECT 
    c.CurrencyCode,
    DATEADD(DAY, -n, GETDATE()),
    0.5 + (ABS(CHECKSUM(NEWID())) % 1000) / 1000.0
FROM (SELECT TOP 100 ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n FROM sys.all_objects) AS days,
     AcmeERP.Currencies c;
