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