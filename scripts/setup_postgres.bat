@echo off
echo Setting up PostgreSQL for Trexim...
echo.

set PGBIN=C:\Program Files\PostgreSQL\18\bin

echo Step 1: Creating database and user...
echo Please enter postgres superuser password when prompted:
echo.

"%PGBIN%\psql" -U postgres -c "CREATE DATABASE trexim;" 2>nul
"%PGBIN%\psql" -U postgres -c "CREATE USER trexim WITH PASSWORD 'trexim2026';" 2>nul
"%PGBIN%\psql" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE trexim TO trexim;" 2>nul
"%PGBIN%\psql" -U postgres -d trexim -c "GRANT ALL ON SCHEMA public TO trexim;" 2>nul

echo.
echo Step 2: Testing connection...
"%PGBIN%\psql" -U trexim -d trexim -c "SELECT 'Connection successful!' as status;" 2>nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo PostgreSQL setup completed successfully!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Run: cd d:\Dev\trexim-v3
    echo 2. Run: alembic upgrade head
    echo 3. Run: python -m uvicorn app.main:app --reload
) else (
    echo.
    echo ========================================
    echo Setup may have issues. Check:
    echo - PostgreSQL service is running
    echo - Correct postgres password
    echo ========================================
)

pause
