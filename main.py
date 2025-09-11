"""
AI Conversation Assistant - Main Application Entry Point
Inspired by Cluely.ai with comprehensive real-time conversation analysis
"""

import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import socketio
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import init_db
from app.core.redis_client import init_redis
from app.api.routes import api_router
from app.services.ai_engine import AIEngine
from app.services.audio_processor import AudioProcessor
from app.services.conversation_analyzer import ConversationAnalyzer
from app.sockets.handlers import register_socket_handlers


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add("logs/app.log", rotation="10 MB", retention="10 days", level="DEBUG")


# Global services
ai_engine = None
audio_processor = None
conversation_analyzer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ai_engine, audio_processor, conversation_analyzer
    
    logger.info("🚀 Starting AI Conversation Assistant...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Initialize Redis
    await init_redis()
    logger.info("✅ Redis initialized")
    
    # Initialize AI services
    ai_engine = AIEngine()
    await ai_engine.initialize()
    logger.info("✅ AI Engine initialized")
    
    audio_processor = AudioProcessor()
    await audio_processor.initialize()
    logger.info("✅ Audio Processor initialized")
    
    conversation_analyzer = ConversationAnalyzer(ai_engine)
    await conversation_analyzer.initialize()
    logger.info("✅ Conversation Analyzer initialized")
    
    # Store services in app state
    app.state.ai_engine = ai_engine
    app.state.audio_processor = audio_processor
    app.state.conversation_analyzer = conversation_analyzer
    
    logger.info("🎉 All services initialized successfully!")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down services...")
    if ai_engine:
        await ai_engine.cleanup()
    if audio_processor:
        await audio_processor.cleanup()
    if conversation_analyzer:
        await conversation_analyzer.cleanup()
    logger.info("✅ Cleanup completed")


# Create FastAPI app
app = FastAPI(
    title="AI Conversation Assistant",
    description="Real-time AI-powered conversation assistant with advanced analytics",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.ALLOWED_ORIGINS,
    logger=True,
    engineio_logger=True
)

# Register socket handlers
register_socket_handlers(sio)

# Combine FastAPI and Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# Include API routes
app.include_router(api_router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "ai_engine": bool(ai_engine and ai_engine.is_ready),
            "audio_processor": bool(audio_processor and audio_processor.is_ready),
            "conversation_analyzer": bool(conversation_analyzer and conversation_analyzer.is_ready)
        }
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Conversation Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    logger.info("🚀 Starting AI Conversation Assistant server...")
    
    uvicorn.run(
        "main:socket_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
        access_log=settings.DEBUG
    )
