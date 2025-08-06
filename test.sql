CREATE PROCEDURE log_hr_employees
AS
BEGIN
    DECLARE @emp_id INT
    DECLARE @emp_name VARCHAR(100)

    -- Declare the cursor
    DECLARE emp_cursor CURSOR FOR
    SELECT emp_id, emp_name
    FROM employees
    WHERE department = 'HR'

    -- Open the cursor
    OPEN emp_cursor

    -- Fetch the first row
    FETCH emp_cursor INTO @emp_id, @emp_name

    -- Loop through the result set
    WHILE @@sqlstatus = 0
    BEGIN
        -- Insert into log table or perform any action
        INSERT INTO employee_log (emp_id, emp_name, log_time)
        VALUES (@emp_id, @emp_name, GETDATE())

        -- Fetch the next row
        FETCH emp_cursor INTO @emp_id, @emp_name
    END

    -- Close and deallocate cursor
    CLOSE emp_cursor
    DEALLOCATE CURSOR emp_cursor
END
GO

CREATE PROCEDURE sp_sum_client_orders
    @client_id INT,
    @from_date DATE,
    @to_date DATE
AS
BEGIN
    DECLARE @grand_total NUMERIC(10,2)
    DECLARE @order_total NUMERIC(10,2)
    DECLARE cur_orders CURSOR FOR
        SELECT total_price FROM client_orders
        WHERE client_id = @client_id
          AND order_date BETWEEN @from_date AND @to_date

    SET @grand_total = 0.00

    OPEN cur_orders
    FETCH cur_orders INTO @order_total

    WHILE @@sqlstatus = 0
    BEGIN
        IF @order_total > 750
        BEGIN
            SET @grand_total = @grand_total + (@order_total * 0.95)
        END
        ELSE
        BEGIN
            SET @grand_total = @grand_total + @order_total
        END

        FETCH cur_orders INTO @order_total
    END

    CLOSE cur_orders
    DEALLOCATE cur_orders

    IF @grand_total > 10000
    BEGIN
        RAISERROR('High-value threshold exceeded for client', 16, 1)
    END

    RETURN @grand_total
END
GO

CREATE PROCEDURE test1
    @client_id INT,
    @from_date DATE,
    @to_date DATE
AS
BEGIN
    DECLARE @grand_total NUMERIC(10,2), @order_total NUMERIC(10,2)

    SET @grand_total = 0.00

    DECLARE cur_orders CURSOR FOR
        SELECT total_price FROM client_orders
        WHERE client_id = @client_id AND order_date BETWEEN @from_date AND @to_date

    OPEN cur_orders
    FETCH NEXT FROM cur_orders INTO @order_total
    WHILE @@FETCH_STATUS = 0
    BEGIN
        IF @order_total > 750
            SET @grand_total = @grand_total + @order_total * 0.95
        ELSE
            SET @grand_total = @grand_total + @order_total

        FETCH NEXT FROM cur_orders INTO @order_total
    END
    CLOSE cur_orders
    DEALLOCATE cur_orders

    IF @grand_total > 10000
        RAISERROR('High-value threshold exceeded for client', 16, 1)

    RETURN @grand_total
END

CREATE PROCEDURE sp_sum_client_orders
    @client_id INT,
    @from_date DATE,
    @to_date DATE
AS
BEGIN
    DECLARE @grand_total NUMERIC(10,2)
    DECLARE @order_total NUMERIC(10,2)
    DECLARE cur_orders CURSOR FOR
        SELECT total_price FROM client_orders
        WHERE client_id = @client_id
          AND order_date BETWEEN @from_date AND @to_date

    SET @grand_total = 0.00

    OPEN cur_orders
    FETCH cur_orders INTO @order_total

    WHILE @@sqlstatus = 0
    BEGIN
        IF @order_total > 750
        BEGIN
            SET @grand_total = @grand_total + (@order_total * 0.95)
        END
        ELSE
        BEGIN
            SET @grand_total = @grand_total + @order_total
        END

        FETCH cur_orders INTO @order_total
    END

    CLOSE cur_orders
    DEALLOCATE cur_orders

    IF @grand_total > 10000
    BEGIN
        RAISERROR('High-value threshold exceeded for client', 16, 1)
    END

    RETURN @grand_total
END
GO

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