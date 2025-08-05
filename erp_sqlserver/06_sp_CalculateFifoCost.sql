-- FIFO cost computation using window function to handle inventory aging
SET QUOTED_IDENTIFIER ON;
GO

IF OBJECT_ID('AcmeERP.usp_CalculateFifoCost', 'P') IS NOT NULL
    DROP PROCEDURE AcmeERP.usp_ProcessPayroll;
GO

CREATE PROCEDURE AcmeERP.usp_CalculateFifoCost
    @ProductID INT,
    @QuantityRequested INT
AS
BEGIN
    WITH CTE_FIFO AS (
        SELECT 
            MovementID,
            ProductID,
            Quantity,
            UnitCost,
            SUM(Quantity) OVER (PARTITION BY ProductID ORDER BY MovementDate ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS RunningTotal
        FROM AcmeERP.StockMovements
        WHERE ProductID = @ProductID AND Direction = 'IN'
    )
    SELECT AVG(UnitCost) AS FifoCostEstimate
    FROM CTE_FIFO
    WHERE RunningTotal <= @QuantityRequested;
END;
GO