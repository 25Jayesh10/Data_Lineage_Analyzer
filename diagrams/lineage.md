```mermaid
graph TD
    %% Node styles
    classDef table fill:#f96,stroke:#333,stroke-width:2px,color:#000;
    classDef stored_proc fill:#9cf,stroke:#333,stroke-width:2px ,color:#000;
    report --> sp_main_report
    sales --> sp_aggregate_sales
    sales --> sp_main_report
    metadata --> sp_fetch_metadata
    metadata --> sp_main_report
    sp_main_report --> sp_aggregate_sales
    sp_main_report --> sp_fetch_metadata
    regions --> sp_aggregate_sales
    audit_log --> sp_fetch_metadata
    audit_log --> sp_log_access
    sp_fetch_metadata --> sp_log_access
    customer --> sp_get_customer
    sp_get_customer --> sp_get_address
    address --> sp_get_address
    orders --> sp_nested_query
    order_items --> sp_nested_query
    products --> sp_nested_query
    products --> sp_update_inventory
    inventory --> sp_update_inventory
    inventory_cursor --> sp_update_inventory
    class sales,products,inventory,orders,metadata,regions,customer,audit_log,inventory_cursor,address,order_items,report table;
    class sp_main_report,sp_nested_query,sp_get_address,sp_log_access,sp_update_inventory,sp_aggregate_sales,sp_fetch_metadata,sp_get_customer stored_proc;
