"""
Database configuration and session management for DecisionTrace.
Handles SQLAlchemy setup, connection pooling, and session lifecycle.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from typing import AsyncGenerator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create declarative base for models
Base = declarative_base()

# Convert PostgreSQL URL to async format if needed
def get_async_database_url(url: str) -> str:
    """Convert standard PostgreSQL URL to async format using psycopg."""
    # psycopg3 uses postgresql+psycopg:// for async
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql+psycopg://"):
        return url
    else:
        raise ValueError(f"Unsupported database URL format: {url}")


# Database URL
DATABASE_URL = get_async_database_url(settings.DATABASE_URL)

# Create async engine with connection pooling
# Connection pool settings:
# - pool_size: Number of connections to maintain in the pool (default: 5)
# - max_overflow: Maximum number of connections that can be created beyond pool_size (default: 10)
# - pool_timeout: Seconds to wait before giving up on getting a connection (default: 30)
# - pool_recycle: Recycle connections after this many seconds (prevents stale connections)
# - pool_pre_ping: Verify connections before using them (helps detect disconnections)
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_size=5,  # Maintain 5 connections in the pool
    max_overflow=10,  # Allow up to 15 total connections (5 + 10)
    pool_timeout=30,  # Wait up to 30 seconds for a connection
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connection health before use
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.
    
    Usage in FastAPI endpoints:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    
    Note: In production, use Alembic migrations instead.
    This is useful for development and testing.
    """
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered with Base
        from app.models import decision  # noqa: F401
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def close_db() -> None:
    """
    Close database connections.
    Should be called on application shutdown.
    """
    await engine.dispose()
    logger.info("Database connections closed")


# Synchronous engine for Alembic migrations
# Using psycopg3 explicitly for Python 3.13 compatibility
sync_database_url = settings.DATABASE_URL
if sync_database_url.startswith("postgresql://"):
    sync_database_url = sync_database_url.replace("postgresql://", "postgresql+psycopg://", 1)

sync_engine = create_engine(
    sync_database_url,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
)

# Synchronous session factory (for Alembic and testing)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


def get_sync_db():
    """
    Get synchronous database session.
    Used for Alembic migrations and testing.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Sync database session error: {e}")
        raise
    finally:
        db.close()
