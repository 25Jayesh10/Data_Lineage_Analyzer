# Summary

- **Total Procedures**: 7
- **Total Tables**: 10
- **Most Called Procedure**: `N/A`

---

# Table of Contents

- [AcmeERP.usp_CalculateFifoCost](#acmeerpusp_calculatefifocost)
- [AcmeERP.usp_ProcessFullPayrollCycle](#acmeerpusp_processfullpayrollcycle)
- [AcmeERP.usp_ConvertToBase](#acmeerpusp_converttobase)
- [sp_sum_client_orders](#sp_sum_client_orders)
- [log_hr_employees](#log_hr_employees)
- [test1](#test1)
- [sp_update_inventory](#sp_update_inventory)

---

## Stored Procedure: AcmeERP.usp_CalculateFifoCost
<a name="acmeerpusp_calculatefifocost"></a>

---

### Parameters

| Name | Type |
|------|------|
| @ProductID | INTEGER |
| @QuantityRequested | INTEGER |

---

### Tables

- AcmeERP.StockMovements
- CTE_FIFO

---

### Called Procedures


---

### Call Graph

```mermaid
graph TD
    AcmeERP.usp_CalculateFifoCost --> AcmeERP.StockMovements
    AcmeERP.usp_CalculateFifoCost --> CTE_FIFO
```

---

### Business Logic

The AcmeERP.usp_CalculateFifoCost stored procedure determines the cost of goods sold for a given product using the First-In, First-Out (FIFO) inventory costing method.  It takes the product ID (`@@ProductID`) and the quantity requested (`@@QuantityRequested`) as input, then calculates the total cost by referencing inventory movements in the `AcmeERP.StockMovements` table and utilizing a common table expression (`CTE_FIFO`) to process inventory based on FIFO principles.  The procedure implicitly returns the total cost associated with fulfilling the order, critical for accurate financial reporting and inventory management.

---


## Stored Procedure: AcmeERP.usp_ProcessFullPayrollCycle
<a name="acmeerpusp_processfullpayrollcycle"></a>

---

### Parameters

| Name | Type |
|------|------|
| @PayPeriodStart | DATE |
| @PayPeriodEnd | DATE |

---

### Tables

- AcmeERP.ExchangeRates
- AcmeERP.PayrollLogs
- #PayrollCalc

---

### Called Procedures


---

### Call Graph

```mermaid
graph TD
    AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.ExchangeRates
    AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.PayrollLogs
    AcmeERP.usp_ProcessFullPayrollCycle --> #PayrollCalc
```

---

### Business Logic

The `AcmeERP.usp_ProcessFullPayrollCycle` stored procedure calculates and processes the complete payroll for a given pay period, defined by the `@@PayPeriodStart` and `@@PayPeriodEnd` parameters.  It uses exchange rate data from `AcmeERP.ExchangeRates` to handle any international payroll elements, logs processing details in `AcmeERP.PayrollLogs`, and utilizes a temporary table, `#PayrollCalc`, for intermediate calculations during the payroll processing. The procedure's purpose is to automate the entire payroll cycle, ensuring accurate and timely compensation for all employees within the specified pay period.

---


## Stored Procedure: AcmeERP.usp_ConvertToBase
<a name="acmeerpusp_converttobase"></a>

---

### Parameters

| Name | Type |
|------|------|
| @CurrencyCode | CHAR |
| @Amount | NUMERIC |
| @ConversionDate | DATE |

---

### Tables

- AcmeERP.ExchangeRates

---

### Called Procedures


---

### Call Graph

```mermaid
graph TD
    AcmeERP.usp_ConvertToBase --> AcmeERP.ExchangeRates
```

---

### Business Logic

The `AcmeERP.usp_ConvertToBase` stored procedure converts a given monetary amount from a specified currency into the base currency of the Acme ERP system.  It uses the exchange rate recorded in the `AcmeERP.ExchangeRates` table on a specified date (`@@ConversionDate`) to perform the conversion. The procedure takes the currency code (`@@CurrencyCode`) and the amount (`@@Amount`) to be converted as input parameters, returning the equivalent value in the base currency.  Error handling (not shown in the provided code) is assumed to manage scenarios like missing exchange rates for the specified date or invalid currency codes.

---


## Stored Procedure: sp_sum_client_orders
<a name="sp_sum_client_orders"></a>

---

### Parameters

| Name | Type |
|------|------|
| @client_id | INTEGER |
| @from_date | DATE |
| @to_date | DATE |

---

### Tables

- client_orders

---

### Called Procedures


---

### Call Graph

```mermaid
graph TD
    sp_sum_client_orders --> client_orders
```

---

### Business Logic

The stored procedure `sp_sum_client_orders` calculates the total value of orders for a given client within a specified date range, applying a 5% discount to orders exceeding $750.  It iterates through the `client_orders` table, summing the `total_price` of each qualifying order.  Orders below $750 are included at their full price, while those above $750 contribute 95% of their value to the final total. The procedure returns the discounted grand total.  Note that the provided code snippet is incomplete; it does not explicitly return the calculated `@grand_total`.

---


## Stored Procedure: log_hr_employees
<a name="log_hr_employees"></a>

---

### Parameters

| Name | Type |
|------|------|

---

### Tables

- employees
- employee_log

---

### Called Procedures


---

### Call Graph

```mermaid
graph TD
    log_hr_employees --> employees
    log_hr_employees --> employee_log
```

---

### Business Logic

The stored procedure `log_hr_employees` automatically logs all HR department employees into the `employee_log` table.  It iterates through each employee in the `employees` table whose department is designated as 'HR', recording their employee ID and name along with the current timestamp. This provides an audit trail of all HR employees, potentially useful for security, reporting, or other HR-related processes requiring a record of active personnel.

---


## Stored Procedure: test1
<a name="test1"></a>

---

### Parameters

| Name | Type |
|------|------|
| @client_id | INTEGER |
| @from_date | DATE |
| @to_date | DATE |

---

### Tables

- client_orders

---

### Called Procedures


---

### Call Graph

```mermaid
graph TD
    test1 --> client_orders
```

---

### Business Logic

Procedure `test1` calculates the total revenue for a given client (`@@client_id`) within a specified date range (`@@from_date` to `@@to_date`).  It iterates through the client's orders in the `client_orders` table.  For orders exceeding 750 currency units, a 5% discount is applied before accumulating the total revenue (`@grand_total`).  Orders less than or equal to 750 are added to the total without discount.  The procedure ultimately returns the total revenue after applying any applicable discounts.

---


## Stored Procedure: sp_update_inventory
<a name="sp_update_inventory"></a>

---

### Parameters

| Name | Type |
|------|------|

---

### Tables

- inventory
- products

---

### Called Procedures


---

### Call Graph

```mermaid
graph TD
    sp_update_inventory --> inventory
    sp_update_inventory --> products
```

---

### Business Logic

The stored procedure `sp_update_inventory` automatically flags products requiring restocking.  It iterates through each active product (discontinued = 0) in the `products` table, summing its current inventory quantity from the `inventory` table. If the total quantity for a product falls below 10 units, the procedure updates the `products` table, setting the `restock` flag to 1 for that product, thereby signaling the need for replenishment to the inventory management system.

---

