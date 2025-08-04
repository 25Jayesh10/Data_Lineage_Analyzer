CREATE PROCEDURE log_high_salary_employees
    @threshold_salary INT
AS
BEGIN
    DECLARE @emp_id INT
    DECLARE @emp_name VARCHAR(100)
    DECLARE @emp_salary INT

    DECLARE emp_cursor CURSOR FOR
    SELECT emp_id, emp_name, salary
    FROM employees
    WHERE salary > @threshold_salary

    OPEN emp_cursor

    FETCH emp_cursor INTO @emp_id, @emp_name, @emp_salary

    WHILE @@SQLSTATUS = 0
    BEGIN
        INSERT INTO high_salary_log(emp_id, emp_name, salary, log_date)
        VALUES (@emp_id, @emp_name, @emp_salary, GETDATE())

        FETCH emp_cursor INTO @emp_id, @emp_name, @emp_salary
    END

    CLOSE emp_cursor
    DEALLOCATE CURSOR emp_cursor
END
