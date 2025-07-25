-- Procedure 1: Simple SELECT with WHERE
CREATE PROCEDURE sp_get_customer_by_id
    @cust_id INT
AS
BEGIN
    SELECT customer_id, customer_name, email
    FROM customers
    WHERE customer_id = @cust_id;
END;
GO

-- Procedure 2: INSERT a new order
CREATE PROCEDURE sp_create_order
    @cust_id INT,
    @amount DECIMAL(10,2)
AS
BEGIN
    INSERT INTO orders (customer_id, order_date, amount)
    VALUES (@cust_id, GETDATE(), @amount);
END;
GO

-- Procedure 3: UPDATE customer email
CREATE PROCEDURE sp_update_customer_email
    @cust_id INT,
    @new_email VARCHAR(100)
AS
BEGIN
    UPDATE customers
    SET email = @new_email
    WHERE customer_id = @cust_id;
END;
GO

-- Procedure 4: SELECT with JOIN
CREATE PROCEDURE sp_get_order_details
    @order_id INT
AS
BEGIN
    SELECT o.order_id, o.order_date, o.amount,
           p.product_name, p.price
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_id = @order_id;
END;
GO

-- Procedure 5: Nested procedure call
CREATE PROCEDURE sp_get_customer_full_details
    @cust_id INT
AS
BEGIN
    EXEC sp_get_customer_by_id @cust_id;
    EXEC sp_get_customer_orders @cust_id;
END;
GO

-- Procedure 6: Procedure that is called above
CREATE PROCEDURE sp_get_customer_orders
    @cust_id INT
AS
BEGIN
    SELECT order_id, order_date, amount
    FROM orders
    WHERE customer_id = @cust_id;
END;
GO

-- Procedure 7: Insert with conditional logic
CREATE PROCEDURE sp_register_or_update_customer
    @cust_id INT,
    @name VARCHAR(100),
    @email VARCHAR(100)
AS
BEGIN
    IF EXISTS (SELECT 1 FROM customers WHERE customer_id = @cust_id)
    BEGIN
        UPDATE customers
        SET customer_name = @name, email = @email
        WHERE customer_id = @cust_id;
    END
    ELSE
    BEGIN
        INSERT INTO customers (customer_id, customer_name, email)
        VALUES (@cust_id, @name, @email);
    END
END;
GO

-- Procedure 8: Transaction example
CREATE PROCEDURE sp_transfer_funds
    @from_cust_id INT,
    @to_cust_id INT,
    @amount DECIMAL(10,2)
AS
BEGIN
    BEGIN TRANSACTION;

    UPDATE customers
    SET balance = balance - @amount
    WHERE customer_id = @from_cust_id;

    UPDATE customers
    SET balance = balance + @amount
    WHERE customer_id = @to_cust_id;

    COMMIT TRANSACTION;
END;
GO
