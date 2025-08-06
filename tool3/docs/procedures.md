# Summary

- **Total Procedures**: 3
- **Total Tables**: 5
- **Most Called Procedure**: `log_order`

---

# Table of Contents

- [process_orders](#process_orders)
- [log_order](#log_order)
- [log_hr_employees](#log_hr_employees)

---

## Stored Procedure: process_orders
<a name="process_orders"></a>

---

### Parameters

| Name | Type |
|------|------|
| order_id | INT |
| customer_id | VARCHAR |

---

### Tables

- orders
- customers

---

### Called Procedures

- log_order
- validate_customer

---

### Call Graph

```mermaid
graph TD
    process_orders --> log_order
    process_orders --> validate_customer
    process_orders --> orders
    process_orders --> customers
```

---

### Business Logic

No description provided.


---


## Stored Procedure: log_order
<a name="log_order"></a>

---

### Parameters

| Name | Type |
|------|------|
| order_id | INT |

---

### Tables

- order_logs

---

### Called Procedures


---

### Call Graph

```mermaid
graph TD
    log_order --> order_logs
```

---

### Business Logic

No description provided.


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

No description provided.


---

