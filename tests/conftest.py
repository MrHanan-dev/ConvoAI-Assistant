"""
Test configuration and fixtures for the entire test suite.
"""
import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.services.ai_engine import AIEngine
from app.services.audio_processor import AudioProcessor
from app.services.conversation_analyzer import ConversationAnalyzer

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create async engine for tests
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_app() -> FastAPI:
    """Create a test instance of the FastAPI application."""
    from main import app
    return app

@pytest.fixture(scope="session")
async def test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for making HTTP requests."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="session")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="session")
async def ai_engine() -> AsyncGenerator[AIEngine, None]:
    """Create a test instance of the AI Engine."""
    engine = AIEngine()
    await engine.initialize()
    yield engine

@pytest.fixture(scope="session")
async def audio_processor() -> AsyncGenerator[AudioProcessor, None]:
    """Create a test instance of the Audio Processor."""
    processor = AudioProcessor()
    await processor.initialize()
    yield processor

@pytest.fixture(scope="session")
async def conversation_analyzer() -> AsyncGenerator[ConversationAnalyzer, None]:
    """Create a test instance of the Conversation Analyzer."""
    analyzer = ConversationAnalyzer()
    await analyzer.initialize()
    yield analyzer

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("COHERE_API_KEY", "test-cohere-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("PINECONE_API_KEY", "test-pinecone-key")
    monkeypatch.setenv("PINECONE_ENVIRONMENT", "test-pinecone-env")
