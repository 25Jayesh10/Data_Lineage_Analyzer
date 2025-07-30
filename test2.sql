CREATE PROCEDURE sp_process_order
    @customer_id INT,
    @order_date DATETIME,
    @item_id INT,
    @quantity INT,
    @order_status VARCHAR(20) OUTPUT
AS
BEGIN
    DECLARE @order_id INT
    DECLARE @available_qty INT

    BEGIN TRANSACTION

    -- Check inventory
    SELECT @available_qty = quantity
    FROM inventory
    WHERE item_id = @item_id

    IF @available_qty < @quantity
    BEGIN
        SET @order_status = 'FAILED - OUT OF STOCK'
        ROLLBACK TRANSACTION
        RETURN
    END

    -- Insert into orders
    INSERT INTO orders (customer_id, order_date)
    VALUES (@customer_id, @order_date)

    SELECT @order_id = @@identity  -- Get the generated order ID

    -- Insert into order_items
    INSERT INTO order_items (order_id, item_id, quantity)
    VALUES (@order_id, @item_id, @quantity)

    -- Update inventory
    UPDATE inventory
    SET quantity = quantity - @quantity
    WHERE item_id = @item_id

    -- Call a logging procedure
    EXEC sp_log_order @order_id, @customer_id, @order_date

    COMMIT TRANSACTION
    SET @order_status = 'SUCCESS'
END
GO
