"""
Database connection and session management
Supports both SQLite (development) and PostgreSQL (production)
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator

try:
    from ..config import settings
except ImportError:
    from config import settings


def get_database_url(async_mode: bool = False) -> str:
    """
    Get database URL based on configuration.
    Converts standard URLs to async-compatible URLs if needed.
    """
    url = settings.DATABASE_URL

    if async_mode:
        # Convert to async driver
        if url.startswith("sqlite:"):
            return url.replace("sqlite:", "sqlite+aiosqlite:")
        elif url.startswith("postgresql:"):
            return url.replace("postgresql:", "postgresql+asyncpg:")
        elif url.startswith("postgres:"):
            return url.replace("postgres:", "postgresql+asyncpg:")

    return url


# Sync engine (for migrations and simple operations)
engine = create_engine(
    get_database_url(async_mode=False),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    # SQLite specific
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Async engine (for production async operations)
async_engine = create_async_engine(
    get_database_url(async_mode=True),
    echo=settings.DEBUG,
    pool_pre_ping=True
)

# Session factories
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


# Dependency for FastAPI - sync
def get_db() -> Generator[Session, None, None]:
    """Get database session (sync)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency for FastAPI - async
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session (async)"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Context managers for manual usage
@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context manager for database session (sync)"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database session (async)"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def init_db():
    """Initialize database tables (for development)"""
    from .models import Base
    Base.metadata.create_all(bind=engine)
