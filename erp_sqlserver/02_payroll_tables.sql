-- Employee and Payroll Tables with Currency Column
CREATE TABLE AcmeERP.Employees (
    EmployeeID INT PRIMARY KEY IDENTITY,
    FirstName NVARCHAR(50),
    LastName NVARCHAR(50),
    Department NVARCHAR(50),
    Position NVARCHAR(50),
    HireDate DATE,
    BaseSalary DECIMAL(18,2),
    Currency CHAR(3) NOT NULL DEFAULT 'USD'
);

CREATE TABLE AcmeERP.PayrollLogs (
    PayrollID INT PRIMARY KEY IDENTITY,
    EmployeeID INT,
    PayPeriodStart DATE,
    PayPeriodEnd DATE,
    GrossSalary DECIMAL(18,2),
    TaxDeducted DECIMAL(18,2),
    NetSalary AS (GrossSalary - TaxDeducted) PERSISTED,
    Paid BIT DEFAULT 0,
    FOREIGN KEY (EmployeeID) REFERENCES AcmeERP.Employees(EmployeeID)
);
