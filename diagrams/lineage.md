```mermaid
graph BT
    %% Node styles
    classDef table fill:#f96,stroke:#333,stroke-width:2px,color:#000;
    classDef stored_proc fill:#9cf,stroke:#333,stroke-width:2px ,color:#000;
    sp_log_order --> sp_process_order
    sp_process_order --> orders
    sp_process_order --> order_items
    sp_process_order --> inventory
    class orders,order_items,inventory table;
    class sp_process_order,sp_log_order stored_proc;
