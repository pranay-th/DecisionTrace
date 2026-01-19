import asyncio
import asyncpg

async def test_connection():
    try:
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/postgres')
        print("✓ PostgreSQL is running and accessible")
        await conn.close()
        return True
    except Exception as e:
        print(f"✗ Cannot connect to PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
