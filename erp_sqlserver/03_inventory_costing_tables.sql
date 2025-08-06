-- Inventory and Costing
CREATE TABLE AcmeERP.Products (
    ProductID INT PRIMARY KEY IDENTITY,
    ProductName NVARCHAR(100),
    Category NVARCHAR(50),
    CostMethod VARCHAR(10) CHECK (CostMethod IN ('FIFO', 'LIFO')),
    CurrentStock INT
);

CREATE TABLE AcmeERP.StockMovements (
    MovementID INT PRIMARY KEY IDENTITY,
    ProductID INT,
    MovementDate DATE,
    Quantity INT,
    UnitCost DECIMAL(18,2),
    Direction VARCHAR(10) CHECK (Direction IN ('IN', 'OUT')),
    FOREIGN KEY (ProductID) REFERENCES AcmeERP.Products(ProductID)
);
