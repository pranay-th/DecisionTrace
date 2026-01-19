"""
Test script for database migrations.
This script tests migration up and down operations and verifies the schema.
"""

import asyncio
import sys
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.database import get_async_database_url

async def test_migrations():
    """Test database migrations."""
    print("=" * 60)
    print("Database Migration Test")
    print("=" * 60)
    
    # Get database URL
    db_url = get_async_database_url(settings.DATABASE_URL)
    print(f"\n1. Connecting to database...")
    print(f"   URL: {db_url.replace(settings.DATABASE_URL.split('@')[0].split('//')[1], '***')}")
    
    try:
        # Create engine
        engine = create_async_engine(db_url, echo=False)
        
        # Test connection
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"   ✓ Connected to PostgreSQL")
            print(f"   Version: {version.split(',')[0]}")
        
        # Check if migrations have been applied
        print(f"\n2. Checking migration status...")
        async with engine.connect() as conn:
            # Check if alembic_version table exists
            result = await conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
            ))
            alembic_exists = result.scalar()
            
            if alembic_exists:
                result = await conn.execute(text("SELECT version_num FROM alembic_version"))
                version_num = result.scalar()
                print(f"   ✓ Current migration: {version_num}")
            else:
                print(f"   ⚠ No migrations applied yet")
                print(f"   Run: alembic upgrade head")
        
        # Check if decisions table exists
        print(f"\n3. Checking decisions table...")
        async with engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'decisions')"
            ))
            table_exists = result.scalar()
            
            if table_exists:
                print(f"   ✓ decisions table exists")
                
                # Get table structure
                result = await conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'decisions'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                
                print(f"\n   Table structure:")
                print(f"   {'Column':<25} {'Type':<20} {'Nullable':<10}")
                print(f"   {'-'*25} {'-'*20} {'-'*10}")
                for col in columns:
                    print(f"   {col[0]:<25} {col[1]:<20} {col[2]:<10}")
                
                # Check indexes
                result = await conn.execute(text("""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = 'decisions'
                    ORDER BY indexname
                """))
                indexes = result.fetchall()
                
                if indexes:
                    print(f"\n   Indexes:")
                    for idx in indexes:
                        print(f"   - {idx[0]}")
                
            else:
                print(f"   ✗ decisions table does not exist")
                print(f"   Run: alembic upgrade head")
        
        await engine.dispose()
        
        print(f"\n{'='*60}")
        print(f"✓ Migration test completed successfully")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print(f"\nMake sure:")
        print(f"  1. PostgreSQL is running")
        print(f"  2. Database 'decisiontrace' exists")
        print(f"  3. DATABASE_URL in .env is correct")
        print(f"  4. Run: docker-compose up -d (if using Docker)")
        return False

async def test_migration_operations():
    """Test migration up and down operations."""
    print("\n" + "=" * 60)
    print("Testing Migration Operations")
    print("=" * 60)
    
    import subprocess
    
    try:
        # Test upgrade
        print("\n1. Testing migration upgrade...")
        result = subprocess.run(
            ["python", "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("   ✓ Migration upgrade successful")
        else:
            print(f"   ✗ Migration upgrade failed: {result.stderr}")
            return False
        
        # Test downgrade
        print("\n2. Testing migration downgrade...")
        result = subprocess.run(
            ["python", "-m", "alembic", "downgrade", "-1"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("   ✓ Migration downgrade successful")
        else:
            print(f"   ✗ Migration downgrade failed: {result.stderr}")
            return False
        
        # Re-apply migration
        print("\n3. Re-applying migration...")
        result = subprocess.run(
            ["python", "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("   ✓ Migration re-applied successfully")
        else:
            print(f"   ✗ Migration re-apply failed: {result.stderr}")
            return False
        
        print(f"\n{'='*60}")
        print(f"✓ All migration operations completed successfully")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during migration operations: {e}")
        return False

if __name__ == "__main__":
    # Run basic migration test
    success = asyncio.run(test_migrations())
    
    if success:
        # If basic test passed, run migration operations test
        print("\nWould you like to test migration operations (up/down)? (y/n): ", end="")
        response = input().strip().lower()
        if response == 'y':
            asyncio.run(test_migration_operations())
    else:
        sys.exit(1)
