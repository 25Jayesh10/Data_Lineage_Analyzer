```mermaid
graph BT
    %% Node styles
    classDef table fill:#f96,stroke:#333,stroke-width:2px,color:#000;
    classDef stored_proc fill:#9cf,stroke:#333,stroke-width:2px ,color:#000;
    sp_log_order --> sp_process_order
    sp_process_order --> inventory
    sp_process_order --> orders
    sp_process_order --> order_items
<<<<<<< Updated upstream
    class orders,order_items,inventory table;
    class sp_log_order,sp_process_order stored_proc;
=======
    class inventory,order_items,orders table;
    class sp_process_order,sp_log_order stored_proc;
>>>>>>> Stashed changes
