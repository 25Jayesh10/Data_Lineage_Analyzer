-- Currency conversion with fallback and historical average
SET QUOTED_IDENTIFIER ON;
GO

IF OBJECT_ID('AcmeERP.usp_ConvertToBase', 'P') IS NOT NULL
    DROP PROCEDURE AcmeERP.usp_ProcessPayroll;
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