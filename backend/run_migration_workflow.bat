@echo off
REM Database Migration Workflow Script for Windows
REM This script demonstrates the complete migration workflow for Task 2.3

echo ==========================================
echo DecisionTrace - Migration Workflow
echo ==========================================
echo.

REM Step 1: Check if Docker is running
echo Step 1: Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running
    echo Please start Docker Desktop and try again
    exit /b 1
)
echo [OK] Docker is running
echo.

REM Step 2: Start PostgreSQL
echo Step 2: Starting PostgreSQL...
docker-compose up -d
echo Waiting for PostgreSQL to be ready...
timeout /t 10 /nobreak >nul

REM Check if PostgreSQL is ready
docker-compose exec -T postgres pg_isready -U postgres >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PostgreSQL failed to start
    echo Check logs with: docker-compose logs postgres
    exit /b 1
)
echo [OK] PostgreSQL is ready
echo.

REM Step 3: Test connection
echo Step 3: Testing database connection...
python test_pg_connection.py
if errorlevel 1 (
    echo [ERROR] Connection failed
    exit /b 1
)
echo [OK] Connection successful
echo.

REM Step 4: Check migration status
echo Step 4: Checking migration status...
python -m alembic current
echo.

REM Step 5: Apply migration
echo Step 5: Applying migration...
python -m alembic upgrade head
if errorlevel 1 (
    echo [ERROR] Migration failed
    exit /b 1
)
echo [OK] Migration applied successfully
echo.

REM Step 6: Verify migration
echo Step 6: Verifying migration...
python test_migrations.py
echo.

REM Step 7: Test rollback
echo Step 7: Testing rollback...
echo Rolling back migration...
python -m alembic downgrade -1
if errorlevel 1 (
    echo [ERROR] Rollback failed
    exit /b 1
)
echo [OK] Rollback successful
echo.

REM Step 8: Re-apply migration
echo Step 8: Re-applying migration...
python -m alembic upgrade head
if errorlevel 1 (
    echo [ERROR] Re-apply failed
    exit /b 1
)
echo [OK] Migration re-applied successfully
echo.

REM Step 9: Final verification
echo Step 9: Final verification...
python test_migrations.py
echo.

REM Summary
echo ==========================================
echo [SUCCESS] All migration tests passed!
echo ==========================================
echo.
echo Migration Details:
echo   - Revision: 6425a63343f6
echo   - Description: Initial schema with decisions table
echo   - Table: decisions
echo   - Indexes: 2 (created_at, updated_at)
echo.
echo Next Steps:
echo   1. Review migration file: alembic\versions\6425a63343f6_*.py
echo   2. Check database: psql decisiontrace
echo   3. Continue with Task 3.1: LLM Client Implementation
echo.
echo To stop PostgreSQL:
echo   docker-compose down
echo.

pause
