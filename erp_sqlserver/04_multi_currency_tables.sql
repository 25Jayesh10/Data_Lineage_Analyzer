-- Currency Tables
CREATE TABLE AcmeERP.Currencies (
    CurrencyCode CHAR(3) PRIMARY KEY,
    CurrencyName NVARCHAR(50)
);

CREATE TABLE AcmeERP.ExchangeRates (
    RateID INT PRIMARY KEY IDENTITY,
    CurrencyCode CHAR(3),
    RateDate DATE,
    RateToBase DECIMAL(18,6),
    FOREIGN KEY (CurrencyCode) REFERENCES AcmeERP.Currencies(CurrencyCode)
);
