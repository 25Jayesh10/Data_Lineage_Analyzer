SET QUOTED_IDENTIFIER ON;
GO

IF OBJECT_ID('AcmeERP.usp_ProcessFullPayrollCycle', 'P') IS NOT NULL
    DROP PROCEDURE AcmeERP.usp_ProcessFullPayrollCycle;
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
