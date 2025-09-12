"""
Database initialization and connection management
"""

import asyncio
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from loguru import logger

from app.core.config import settings

# Create the declarative base
Base = declarative_base()

# Global variables
async_engine = None
async_session_maker = None
metadata = MetaData()


async def init_db():
    """Initialize database connection and create tables"""
    global async_engine, async_session_maker
    
    try:
        # Create async engine with fallback to SQLite
        database_url = settings.DATABASE_URL
        
        # Try to use configured database first
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
        elif database_url.startswith('sqlite://'):
            database_url = database_url.replace('sqlite://', 'sqlite+aiosqlite://')
        
        try:
            async_engine = create_async_engine(
                database_url,
                poolclass=NullPool,
                echo=settings.DEBUG,
            )
            # Test connection
            async with async_engine.begin() as conn:
                pass
        except Exception as db_error:
            logger.warning(f"Failed to connect to configured database: {db_error}")
            logger.info("Falling back to SQLite database...")
            database_url = "sqlite+aiosqlite:///./ai_assistant.db"
            async_engine = create_async_engine(
                database_url,
                poolclass=NullPool,
                echo=settings.DEBUG,
            )
        
        # Create session maker
        async_session_maker = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Import all models to ensure they are registered
        from app.models import user, conversation, document, team, integration, objection_template, playbook, call_shadow, audit_log
        
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.success(f"Database initialized successfully! Using: {database_url}")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def get_db():
    """Get database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def close_db():
    """Close database connections"""
    global async_engine
    if async_engine:
        await async_engine.dispose()
        logger.info("Database connections closed")
