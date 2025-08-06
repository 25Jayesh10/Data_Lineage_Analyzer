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
