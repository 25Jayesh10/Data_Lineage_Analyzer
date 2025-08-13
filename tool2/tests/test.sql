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

CREATE PROCEDURE AcmeERP.usp_ProcessFullPayrollCycle
    @PayPeriodStart DATE,
    @PayPeriodEnd DATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Start transaction for payroll processing
    BEGIN TRY
        BEGIN TRANSACTION;

        -- Declare variables for processing
        DECLARE @EmployeeID INT;
        DECLARE @BaseSalary DECIMAL(18,2);
        DECLARE @Bonus DECIMAL(18,2);
        DECLARE @GrossSalary DECIMAL(18,2);
        DECLARE @Tax DECIMAL(18,2);
        DECLARE @NetSalary DECIMAL(18,2);
        DECLARE @Currency CHAR(3);
        DECLARE @ConvertedSalary DECIMAL(18,2);
        DECLARE @ExchangeRate DECIMAL(18,6);
        DECLARE @CurrentDate DATE = GETDATE();

        -- Create a temporary table to store payroll calculations
        IF OBJECT_ID('tempdb..#PayrollCalc') IS NOT NULL
            DROP TABLE #PayrollCalc;
        CREATE TABLE #PayrollCalc (
            EmployeeID INT,
            BaseSalary DECIMAL(18,2),
            Bonus DECIMAL(18,2),
            GrossSalary DECIMAL(18,2),
            Tax DECIMAL(18,2),
            NetSalary DECIMAL(18,2),
            Currency CHAR(3),
            ConvertedSalary DECIMAL(18,2)
        );

        -- Insert calculated payroll values per employee
        INSERT INTO #PayrollCalc (EmployeeID, BaseSalary, Bonus, GrossSalary, Tax, NetSalary, Currency)
        SELECT 
            e.EmployeeID,
            e.BaseSalary,
            CASE 
                WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 10 THEN e.BaseSalary * 0.15
                WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 5 THEN e.BaseSalary * 0.10
                WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 2 THEN e.BaseSalary * 0.05
                ELSE 0
            END AS Bonus,
            e.BaseSalary +
            CASE 
                WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 10 THEN e.BaseSalary * 0.15
                WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 5 THEN e.BaseSalary * 0.10
                WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 2 THEN e.BaseSalary * 0.05
                ELSE 0
            END AS GrossSalary,
            CASE 
                WHEN e.BaseSalary <= 50000 THEN e.BaseSalary * 0.1
                WHEN e.BaseSalary <= 75000 THEN e.BaseSalary * 0.15
                ELSE e.BaseSalary * 0.2
            END AS Tax,
            (e.BaseSalary +
            CASE 
                WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 10 THEN e.BaseSalary * 0.15
                WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 5 THEN e.BaseSalary * 0.10
                WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 2 THEN e.BaseSalary * 0.05
                ELSE 0
            END) -
            CASE 
                WHEN e.BaseSalary <= 50000 THEN e.BaseSalary * 0.1
                WHEN e.BaseSalary <= 75000 THEN e.BaseSalary * 0.15
                ELSE e.BaseSalary * 0.2
            END AS NetSalary,
            ISNULL(e.Currency, 'USD') AS Currency
        FROM AcmeERP.Employees e;

        -- Declare a cursor for payroll processing (for currency conversion)
        DECLARE PayrollCursor CURSOR FAST_FORWARD FOR 
            SELECT EmployeeID, GrossSalary, Currency
            FROM #PayrollCalc;
        OPEN PayrollCursor;
        FETCH NEXT FROM PayrollCursor INTO @EmployeeID, @GrossSalary, @Currency;
        WHILE @@FETCH_STATUS = 0
        BEGIN
            IF @Currency <> 'USD'
            BEGIN
                -- Retrieve the latest exchange rate for the employee's currency
                SELECT TOP 1 @ExchangeRate = RateToBase
                FROM AcmeERP.ExchangeRates
                WHERE CurrencyCode = @Currency AND RateDate <= @CurrentDate
                ORDER BY RateDate DESC;
                IF @ExchangeRate IS NULL SET @ExchangeRate = 1;
                SET @ConvertedSalary = @GrossSalary * @ExchangeRate;
            END
            ELSE
            BEGIN
                SET @ConvertedSalary = @GrossSalary;
            END;

            -- Update the temporary table with converted salary
            UPDATE #PayrollCalc
            SET ConvertedSalary = @ConvertedSalary
            WHERE EmployeeID = @EmployeeID;

            FETCH NEXT FROM PayrollCursor INTO @EmployeeID, @GrossSalary, @Currency;
        END;
        CLOSE PayrollCursor;
        DEALLOCATE PayrollCursor;

        -- Insert the calculated payroll into the PayrollLogs table
        INSERT INTO AcmeERP.PayrollLogs (EmployeeID, PayPeriodStart, PayPeriodEnd, GrossSalary, TaxDeducted)
        SELECT EmployeeID, @PayPeriodStart, @PayPeriodEnd, ConvertedSalary, Tax
        FROM #PayrollCalc;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        DECLARE @ErrorMsg NVARCHAR(4000), @ErrorSeverity INT, @ErrorState INT;
        SELECT 
            @ErrorMsg = ERROR_MESSAGE(),
            @ErrorSeverity = ERROR_SEVERITY(),
            @ErrorState = ERROR_STATE();
        RAISERROR (@ErrorMsg, @ErrorSeverity, @ErrorState);
    END CATCH
END
GO

CREATE PROCEDURE AcmeERP.usp_ConvertToBase
    @CurrencyCode CHAR(3),
    @Amount DECIMAL(18,2),
    @ConversionDate DATE
AS
BEGIN
    DECLARE @Rate DECIMAL(18,6);

    -- Attempt to get exact match
    SELECT @Rate = RateToBase
    FROM AcmeERP.ExchangeRates
    WHERE CurrencyCode = @CurrencyCode AND RateDate = @ConversionDate;

    -- If not found, get most recent before the date
    IF @Rate IS NULL
    BEGIN
        SELECT TOP 1 @Rate = RateToBase
        FROM AcmeERP.ExchangeRates
        WHERE CurrencyCode = @CurrencyCode AND RateDate < @ConversionDate
        ORDER BY RateDate DESC;
    END

    -- If still not found, use average of last 7 days
    IF @Rate IS NULL
    BEGIN
        SELECT @Rate = AVG(RateToBase)
        FROM AcmeERP.ExchangeRates
        WHERE CurrencyCode = @CurrencyCode AND RateDate BETWEEN DATEADD(DAY, -7, @ConversionDate) AND @ConversionDate;
    END

    -- Final fallback
    IF @Rate IS NULL SET @Rate = 1;

    SELECT @Amount * @Rate AS ConvertedAmount;
END;
GO

CREATE PROCEDURE sp_sum_client_orders
    @client_id INT,
    @from_date DATE,
    @to_date DATE
AS
BEGIN
    DECLARE @grand_total NUMERIC(10,2)
    DECLARE @order_total NUMERIC(10,2)
    DECLARE cur_orders CURSOR FOR
        SELECT total_price FROM client_orders
        WHERE client_id = @client_id
          AND order_date BETWEEN @from_date AND @to_date

    SET @grand_total = 0.00

    OPEN cur_orders
    FETCH cur_orders INTO @order_total

    WHILE @@sqlstatus = 0
    BEGIN
        IF @order_total > 750
        BEGIN
            SET @grand_total = @grand_total + (@order_total * 0.95)
        END
        ELSE
        BEGIN
            SET @grand_total = @grand_total + @order_total
        END

        FETCH cur_orders INTO @order_total
    END

    CLOSE cur_orders
    DEALLOCATE cur_orders

    IF @grand_total > 10000
    BEGIN
        RAISERROR('High-value threshold exceeded for client', 16,1)
    END

    RETURN @grand_total
END
GO

CREATE PROCEDURE log_hr_employees
AS
BEGIN
    DECLARE @emp_id INT
    DECLARE @emp_name VARCHAR(100)

    -- Declare the cursor
    DECLARE emp_cursor CURSOR FOR
    SELECT emp_id, emp_name
    FROM employees
    WHERE department = 'HR'

    -- Open the cursor
    OPEN emp_cursor

    -- Fetch the first row
    FETCH emp_cursor INTO @emp_id, @emp_name

    -- Loop through the result set
    WHILE @@sqlstatus = 0
    BEGIN
        -- Insert into log table or perform any action
        INSERT INTO employee_log (emp_id, emp_name, log_time)
        VALUES (@emp_id, @emp_name, GETDATE())

        -- Fetch the next row
        FETCH emp_cursor INTO @emp_id, @emp_name
    END

    -- Close and deallocate cursor
    CLOSE emp_cursor
    DEALLOCATE CURSOR emp_cursor
END
GO

CREATE PROCEDURE test1
    @client_id INT,
    @from_date DATE,
    @to_date DATE
AS
BEGIN
    DECLARE @grand_total NUMERIC(10,2), @order_total NUMERIC(10,2)

    SET @grand_total = 0.00

    DECLARE cur_orders CURSOR FOR
        SELECT total_price FROM client_orders
        WHERE client_id = @client_id AND order_date BETWEEN @from_date AND @to_date

    OPEN cur_orders
    FETCH NEXT FROM cur_orders INTO @order_total
    WHILE @@FETCH_STATUS = 0
    BEGIN
        IF @order_total > 750
            SET @grand_total = @grand_total + @order_total * 0.95
        ELSE
            SET @grand_total = @grand_total + @order_total

        FETCH NEXT FROM cur_orders INTO @order_total
    END
    CLOSE cur_orders
    DEALLOCATE cur_orders

    IF @grand_total > 10000
        RAISERROR('High-value threshold exceeded for client', 16, 1)

    RETURN @grand_total
END

CREATE PROCEDURE sp_sum_client_orders
    @client_id INT,
    @from_date DATE,
    @to_date DATE
AS
BEGIN
    DECLARE @grand_total NUMERIC(10,2)
    DECLARE @order_total NUMERIC(10,2)
    DECLARE cur_orders CURSOR FOR
        SELECT total_price FROM client_orders
        WHERE client_id = @client_id
          AND order_date BETWEEN @from_date AND @to_date

    SET @grand_total = 0.00

    OPEN cur_orders
    FETCH cur_orders INTO @order_total

    WHILE @@sqlstatus = 0
    BEGIN
        IF @order_total > 750
        BEGIN
            SET @grand_total = @grand_total + (@order_total * 0.95)
        END
        ELSE
        BEGIN
            SET @grand_total = @grand_total + @order_total
        END

        FETCH cur_orders INTO @order_total
    END

    CLOSE cur_orders
    DEALLOCATE cur_orders

    IF @grand_total > 10000
    BEGIN
        RAISERROR('High-value threshold exceeded for client', 16,1)
    END

    RETURN @grand_total
END
GO

CREATE PROCEDURE sp_update_inventory
AS
BEGIN
    DECLARE @product_id INT, @quantity INT;
    DECLARE inventory_cursor CURSOR FOR
        SELECT product_id FROM products WHERE discontinued = 0;

    OPEN inventory_cursor;
    FETCH NEXT FROM inventory_cursor INTO @product_id;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        SELECT @quantity = SUM(quantity) FROM inventory WHERE product_id = @product_id;

        IF @quantity < 10
        BEGIN
            UPDATE products SET restock = 1 WHERE product_id = @product_id;
        END

        FETCH NEXT FROM inventory_cursor INTO @product_id;
    END

    CLOSE inventory_cursor;
    DEALLOCATE inventory_cursor;
END