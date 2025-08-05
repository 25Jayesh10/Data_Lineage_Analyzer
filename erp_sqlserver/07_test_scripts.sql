SET QUOTED_IDENTIFIER ON;
GO
-- Test full payroll processing cycle
PRINT 'Running Full Payroll Processing Cycle (usp_ProcessFullPayrollCycle)...';
EXEC AcmeERP.usp_ProcessFullPayrollCycle @PayPeriodStart = '2024-12-01', @PayPeriodEnd = '2024-12-31';
GO

-- Validate payroll logs (after full payroll cycle)
SELECT TOP 10 * FROM AcmeERP.PayrollLogs ORDER BY PayrollID DESC;
GO

-- Test FIFO costing
PRINT 'Calculating FIFO Cost for ProductID = 1, Quantity = 10...';
EXEC AcmeERP.usp_CalculateFifoCost @ProductID = 1, @QuantityRequested = 10;
GO

-- Test currency conversion for EUR
DECLARE @Today DATE = CAST(GETDATE() AS DATE);

PRINT 'Converting 100 EUR on latest available date...';
EXEC AcmeERP.usp_ConvertToBase 
    @CurrencyCode = 'EUR', 
    @Amount = 100, 
    @ConversionDate = @Today;
GO

-- Validate currency conversion for other currencies
PRINT 'Converting 5000 INR on 2024-12-15...';
EXEC AcmeERP.usp_ConvertToBase @CurrencyCode = 'INR', @Amount = 5000, @ConversionDate = '2024-12-15';
GO

PRINT 'Converting 10000 JPY on 2024-12-10...';
EXEC AcmeERP.usp_ConvertToBase @CurrencyCode = 'JPY', @Amount = 10000, @ConversionDate = '2024-12-10';
GO

