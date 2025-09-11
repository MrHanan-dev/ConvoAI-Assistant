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
        # Create async engine
        async_engine = create_async_engine(
            settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'),
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
        
        logger.success("Database initialized successfully!")
        
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
