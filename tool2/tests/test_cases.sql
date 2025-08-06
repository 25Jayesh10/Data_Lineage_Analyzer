CREATE PROCEDURE dbo.sp_ProcessShipments
    @BatchID INT,
    @ProcessedCount INT OUTPUT
AS
BEGIN
    DECLARE @ShipmentID INT, @Status VARCHAR(50)
    DECLARE shipment_cursor CURSOR FOR
        SELECT ShipmentID FROM Shipments WHERE BatchID = @BatchID AND Status = 'Pending'

    SET @ProcessedCount = 0

    BEGIN TRY
        OPEN shipment_cursor
        FETCH NEXT FROM shipment_cursor INTO @ShipmentID

        WHILE @@FETCH_STATUS = 0
        BEGIN
            UPDATE Shipments
            SET Status = 'Shipped'
            WHERE ShipmentID = @ShipmentID

            SET @ProcessedCount = @ProcessedCount + 1
            FETCH NEXT FROM shipment_cursor INTO @ShipmentID
        END

        CLOSE shipment_cursor
        DEALLOCATE shipment_cursor
    END TRY
    BEGIN CATCH
        IF CURSOR_STATUS('global', 'shipment_cursor') >= -1
        BEGIN
            CLOSE shipment_cursor
            DEALLOCATE shipment_cursor
        END
        RETURN -1
    END CATCH

    RETURN 0
END
GO

CREATE PROCEDURE dbo.sp_ApplyDiscounts
    @CustomerID INT,
    @DiscountRate DECIMAL(5,2)
AS
BEGIN
    BEGIN TRANSACTION

    IF EXISTS (SELECT 1 FROM Customers WHERE CustomerID = @CustomerID AND IsActive = 1)
    BEGIN
        IF @DiscountRate BETWEEN 0 AND 50
        BEGIN
            UPDATE Orders
            SET Discount = @DiscountRate
            WHERE CustomerID = @CustomerID AND OrderDate >= DATEADD(month, -6, GETDATE())
        END
        ELSE
        BEGIN
            PRINT 'Invalid discount rate'
            ROLLBACK TRANSACTION
            RETURN -1
        END
    END
    ELSE
    BEGIN
        PRINT 'Customer not found or inactive'
        ROLLBACK TRANSACTION
        RETURN -1
    END

    COMMIT TRANSACTION
    RETURN 0
END
GO

CREATE PROCEDURE dbo.sp_ExecuteDynamicQuery
    @TableName VARCHAR(100),
    @RowCount INT OUTPUT
AS
BEGIN
    DECLARE @SQL NVARCHAR(500)

    SET @SQL = 'SELECT COUNT(*) FROM ' + QUOTENAME(@TableName)
    EXEC sp_executesql @SQL, N'@RowCount INT OUTPUT', @RowCount OUTPUT

    IF @RowCount = 0
    BEGIN
        EXEC dbo.sp_LogEmptyTable @TableName
    END

    RETURN 0
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
    @client_id INTEGER,
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

CREATE PROCEDURE process_customer_orders
    @customer_id INT,
    @order_summary VARCHAR(255) OUTPUT
AS
BEGIN
    DECLARE @order_id INT;
    DECLARE @order_amount NUMERIC(10, 2);
    DECLARE @status VARCHAR(20);
    DECLARE @sql_query TEXT;
    DECLARE @exists_flag INT;

    -- Declare a Temp Table
    CREATE TABLE #order_temp (
        order_id INT,
        order_amount NUMERIC(10, 2)
    );

    -- Check if customer has orders
    SELECT @exists_flag = COUNT(*)
    FROM orders
    WHERE customer_id = @customer_id;

    IF @exists_flag > 0
    BEGIN
        DECLARE order_cursor CURSOR FOR
        SELECT order_id, total_amount
        FROM orders
        WHERE customer_id = @customer_id;

        OPEN order_cursor;
        FETCH NEXT FROM order_cursor INTO @order_id, @order_amount;

        WHILE @@FETCH_STATUS = 0
        BEGIN
            -- CASE WHEN logic
            IF @order_amount > 1000
                SET @status = 'HighValue';
            ELSE IF @order_amount <= 1000
                SET @status = 'Normal';
            ELSE
                SET @status = 'Unknown';

            -- TRY-CATCH for dynamic SQL update
            BEGIN TRY
                SET @sql_query = 'UPDATE orders SET status = ''' + @status + ''' WHERE order_id = ' + CAST(@order_id AS VARCHAR);
                EXEC(@sql_query);
            END TRY
            BEGIN CATCH
                RAISERROR('Failed to update status dynamically.', 16, 1);
            END CATCH

            -- Execute log_order_activity procedure
            EXEC log_order_activity @order_id, @status;

            FETCH NEXT FROM order_cursor INTO @order_id, @order_amount;
        END

        CLOSE order_cursor;
        DEALLOCATE order_cursor;

        -- Prepare order summary
        SELECT @order_summary = 'Processed ' + CAST(COUNT(*) AS VARCHAR) + ' orders.'
        FROM orders
        WHERE customer_id = @customer_id;
    END
    ELSE
    BEGIN
        PRINT 'No orders found for the given customer.';
        SET @order_summary = 'No orders found.';
    END

    -- TRY-CATCH around finalizing
    BEGIN TRY
        EXEC finalize_customer_summary @customer_id, @order_summary;
    END TRY
    BEGIN CATCH
        PRINT 'Failed to finalize customer summary.';
        RETURN -1;
    END CATCH

    RETURN 0;
END
GO

CREATE PROCEDURE ultimate_edge_case_proc
    @user_id INTEGER,
    @result_msg TEXT OUTPUT
AS
BEGIN
    DECLARE @loop_counter INTEGER
    DECLARE @temp_value NUMERIC(10,2)
    DECLARE @status_flag INTEGER
    DECLARE @dynamic_sql TEXT

    -- Temp Table Declaration
    CREATE TABLE #TempTable (
        temp_col INTEGER
    )

    -- Check if user exists
    SELECT @status_flag = COUNT(*)
    FROM users
    WHERE id = @user_id

    IF @status_flag > 0
    BEGIN
        -- Loop Example
        SET @loop_counter = 0
        WHILE @loop_counter < 5
        BEGIN
            SET @loop_counter = @loop_counter + 1

            -- Dynamic SQL Execution
            SET @dynamic_sql = 'UPDATE logs SET status = ''processed'' WHERE user_id = ' + CAST(@user_id AS VARCHAR) + ' AND attempt = ' + CAST(@loop_counter AS VARCHAR)
            EXEC (@dynamic_sql)

            -- CASE WHEN Example (to be flattened)
            IF @loop_counter = 3
            BEGIN
                SET @temp_value = 999.99
            END
            ELSE IF @loop_counter > 3
            BEGIN
                SET @temp_value = 123.45
            END
            ELSE
            BEGIN
                SET @temp_value = 0.00
            END

            -- TRY-CATCH Block Simulation
            BEGIN TRY
                EXEC log_attempt @user_id, @loop_counter
            END TRY
            BEGIN CATCH
                RAISERROR('Logging attempt failed!', 16, 1)
            END CATCH
        END
    END
    ELSE
    BEGIN
        SET @result_msg = 'User does not exist.'
    END

    -- Cursor Declaration
    DECLARE user_cursor CURSOR FOR
    SELECT id, name
    FROM users
    WHERE active = 1

    OPEN user_cursor

    DECLARE @cursor_user_id INTEGER
    DECLARE @cursor_user_name TEXT

    FETCH NEXT FROM user_cursor INTO @cursor_user_id, @cursor_user_name

    WHILE @@FETCH_STATUS = 0
    BEGIN
        INSERT INTO audit_log (user_id, message)
        VALUES (@cursor_user_id, @cursor_user_name)

        FETCH NEXT FROM user_cursor INTO @cursor_user_id, @cursor_user_name
    END

    CLOSE user_cursor
    DEALLOCATE user_cursor

    -- Exception Handling Block Simulation
    BEGIN TRY
        EXEC finalize_process @user_id
    END TRY
    BEGIN CATCH
        PRINT 'Failed to finalize process.'
        RETURN -1
    END CATCH

    RETURN 0
END
GO