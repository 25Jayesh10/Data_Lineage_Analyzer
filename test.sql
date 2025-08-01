CREATE PROCEDURE archive_inactive_users
AS
BEGIN
    DECLARE @user_id INT

    SELECT TOP 1 @user_id = user_id
    FROM users
    WHERE active = 0

    IF @user_id IS NOT NULL
    BEGIN
        INSERT INTO archived_users (user_id, archived_at)
        VALUES (@user_id, GETDATE())
    END
END
GO
