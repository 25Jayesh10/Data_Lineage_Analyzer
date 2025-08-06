# Summary

- **Total Procedures**: 4
- **Total Tables**: 5
- **Most Called Procedure**: `N/A`

---

# Table of Contents

- [log_hr_employees](#log_hr_employees)
- [sp_sum_client_orders](#sp_sum_client_orders)
- [test1](#test1)
- [sp_update_inventory](#sp_update_inventory)

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

No description provided.


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

No description provided.


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

No description provided.


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

No description provided.


---

