CREATE PROCEDURE sp_update_inventory
AS
BEGIN
    DECLARE @product_id INT, @quantity INT;
    DECLARE inventory_cursor CURSOR FOR
        SELECT product_id FROM products WHERE discontinued = 0;

    OPEN inventory_cursor;
    FETCH NEXT FROM inventory_cursor INTO @product_id;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        SELECT @quantity = SUM(quantity) FROM inventory WHERE product_id = @product_id;

        IF @quantity < 10
        BEGIN
            UPDATE products SET restock = 1 WHERE product_id = @product_id;
        END

        FETCH NEXT FROM inventory_cursor INTO @product_id;
    END

    CLOSE inventory_cursor;
    DEALLOCATE inventory_cursor;
END