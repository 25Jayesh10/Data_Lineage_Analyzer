```mermaid
graph BT
    %% Node styles
    classDef table fill:#f96,stroke:#333,stroke-width:2px,color:#000;
    classDef stored_proc fill:#9cf,stroke:#333,stroke-width:2px ,color:#000;
    log_hr_employees --> employee_log
    log_hr_employees --> employees
    log_high_salary_employees --> high_salary_log
    class high_salary_log,employees,employee_log table;
    class log_hr_employees,log_high_salary_employees stored_proc;
```