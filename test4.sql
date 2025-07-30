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
        RAISERROR 'High-value threshold exceeded for client'
    END

    RETURN @grand_total
END
GO