"""
Test script to verify database setup and connection pooling.
Run this script to ensure the database configuration is working correctly.
"""

import asyncio
import sys
from sqlalchemy import text
from app.database import engine, AsyncSessionLocal, get_async_database_url
from app.config import settings


async def test_database_connection():
    """Test basic database connectivity."""
    print("Testing database connection...")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Async URL: {get_async_database_url(settings.DATABASE_URL)}")
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Connected to PostgreSQL")
            print(f"  Version: {version}")
            return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


async def test_session_creation():
    """Test session creation and basic query."""
    print("\nTesting session creation...")
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1 as test"))
            value = result.scalar()
            assert value == 1
            print(f"✓ Session created successfully")
            print(f"  Test query result: {value}")
            return True
    except Exception as e:
        print(f"✗ Session creation failed: {e}")
        return False


async def test_connection_pool():
    """Test connection pooling by creating multiple concurrent sessions."""
    print("\nTesting connection pool...")
    
    async def query_task(task_id: int):
        """Execute a simple query."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(text(f"SELECT {task_id} as id"))
            return result.scalar()
    
    try:
        # Create 10 concurrent tasks (more than pool_size of 5)
        tasks = [query_task(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert results == list(range(10))
        print(f"✓ Connection pool working correctly")
        print(f"  Executed {len(results)} concurrent queries")
        return True
    except Exception as e:
        print(f"✗ Connection pool test failed: {e}")
        return False


async def test_pool_settings():
    """Display connection pool settings."""
    print("\nConnection Pool Settings:")
    print(f"  Pool size: {engine.pool.size()}")
    print(f"  Pool timeout: {engine.pool._timeout}")
    print(f"  Pool recycle: {engine.pool._recycle}")
    print(f"  Pool pre-ping: {engine.pool._pre_ping}")
    print(f"  Max overflow: {engine.pool._max_overflow}")


async def main():
    """Run all database tests."""
    print("=" * 60)
    print("DecisionTrace Database Setup Verification")
    print("=" * 60)
    
    tests = [
        test_database_connection(),
        test_session_creation(),
        test_connection_pool(),
    ]
    
    results = await asyncio.gather(*tests)
    
    await test_pool_settings()
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All tests passed!")
        print("Database setup is working correctly.")
        print("\nNext steps:")
        print("1. Create your models in app/models/")
        print("2. Generate migrations: alembic revision --autogenerate -m 'Initial schema'")
        print("3. Apply migrations: alembic upgrade head")
        return 0
    else:
        print("✗ Some tests failed!")
        print("Please check your database configuration and ensure PostgreSQL is running.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
