```mermaid
graph BT
    %% Node styles
    classDef table fill:#f96,stroke:#333,stroke-width:2px,color:#000;
    classDef stored_proc fill:#9cf,stroke:#333,stroke-width:2px ,color:#000;
<<<<<<< HEAD
    AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.PayrollLogs
    AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.ExchangeRates
    AcmeERP.usp_ProcessFullPayrollCycle --> #PayrollCalc
    AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.Employees
    class AcmeERP.PayrollLogs,AcmeERP.ExchangeRates,AcmeERP.Employees,#PayrollCalc table;
    class AcmeERP.usp_ProcessFullPayrollCycle stored_proc;
=======
    log_hr_employees --> employee_log
    log_hr_employees --> employees
    sp_sum_client_orders --> client_orders
    test1 --> client_orders
    sp_update_inventory --> inventory
    sp_update_inventory --> products
    log_hr_employees --> sp_process_and_log
    sp_sum_client_orders --> sp_process_and_log
    class inventory,employee_log,client_orders,products,employees table;
    class log_hr_employees,sp_process_and_log,sp_sum_client_orders,test1,sp_update_inventory stored_proc;
>>>>>>> main
```