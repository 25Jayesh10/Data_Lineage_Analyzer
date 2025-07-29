```mermaid
graph BT
    %% Node styles
    classDef table fill:#f96,stroke:#333,stroke-width:2px,color:#000;
    classDef stored_proc fill:#9cf,stroke:#333,stroke-width:2px ,color:#000;
    sp_log_order --> sp_process_order
    sp_process_order --> orders
    sp_process_order --> inventory
    sp_process_order --> order_items
    class orders,inventory,order_items table;
    class sp_log_order,sp_process_order stored_proc;
