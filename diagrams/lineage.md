```mermaid
graph BT
    %% Node styles
    classDef table fill:#f96,stroke:#333,stroke-width:2px,color:#000;
    classDef stored_proc fill:#9cf,stroke:#333,stroke-width:2px ,color:#000;
    class inventory,order_items,orders table;
    class sp_process_order,sp_log_order stored_proc;
=======
    sp_sum_client_orders --> client_orders
    class client_orders table;
    class sp_sum_client_orders stored_proc;
```
>>>>>>> Stashed changes
