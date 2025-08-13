# Summary

- **Total Procedures**: 7
- **Total Tables**: 9
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

- CTE_FIFO

---

### Called Procedures


---

### Call Graph

```mermaid
graph TD
    AcmeERP.usp_CalculateFifoCost --> CTE_FIFO
```

---

### Business Logic

Description could not be generated due to an error.


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

- AcmeERP.PayrollLogs
- AcmeERP.ExchangeRates
- #PayrollCalc

---

### Called Procedures


---

### Call Graph

```mermaid
graph TD
    AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.PayrollLogs
    AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.ExchangeRates
    AcmeERP.usp_ProcessFullPayrollCycle --> #PayrollCalc
```

---

### Business Logic

Description could not be generated due to an error.


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

Description could not be generated due to an error.


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

Description could not be generated due to an error.


---


## Stored Procedure: log_hr_employees
<a name="log_hr_employees"></a>

---

### Parameters

| Name | Type |
|------|------|

---

### Tables

- employee_log
- employees

---

### Called Procedures


---

### Call Graph

```mermaid
graph TD
    log_hr_employees --> employee_log
    log_hr_employees --> employees
```

---

### Business Logic

Description could not be generated due to an error.


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

Description could not be generated due to an error.


---


## Stored Procedure: sp_update_inventory
<a name="sp_update_inventory"></a>

---

### Parameters

| Name | Type |
|------|------|

---

### Tables

- products
- inventory

---

### Called Procedures


---

### Call Graph

```mermaid
graph TD
    sp_update_inventory --> products
    sp_update_inventory --> inventory
```

---

### Business Logic

Description could not be generated due to an error.


---

