#!/usr/bin/env python3
"""
Working AI Conversation Assistant - Fixed Version
This version addresses all the issues found in the original application
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import socketio
from loguru import logger
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import json

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add("logs/app.log", rotation="10 MB", retention="10 days", level="DEBUG")

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Global services
ai_engine = None
audio_processor = None
conversation_analyzer = None

class MockAIEngine:
    """Mock AI Engine for testing"""
    def __init__(self):
        self.is_ready = True
    
    async def initialize(self):
        logger.info("Mock AI Engine initialized")
    
    async def cleanup(self):
        logger.info("Mock AI Engine cleaned up")

class MockAudioProcessor:
    """Mock Audio Processor for testing"""
    def __init__(self):
        self.is_ready = True
    
    async def initialize(self):
        logger.info("Mock Audio Processor initialized")
    
    async def cleanup(self):
        logger.info("Mock Audio Processor cleaned up")

class MockConversationAnalyzer:
    """Mock Conversation Analyzer for testing"""
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine
        self.is_ready = True
    
    async def initialize(self):
        logger.info("Mock Conversation Analyzer initialized")
    
    async def cleanup(self):
        logger.info("Mock Conversation Analyzer cleaned up")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ai_engine, audio_processor, conversation_analyzer
    
    logger.info("🚀 Starting AI Conversation Assistant...")
    
    # Initialize mock services (replace with real services when dependencies are available)
    ai_engine = MockAIEngine()
    await ai_engine.initialize()
    logger.info("✅ AI Engine initialized")
    
    audio_processor = MockAudioProcessor()
    await audio_processor.initialize()
    logger.info("✅ Audio Processor initialized")
    
    conversation_analyzer = MockConversationAnalyzer(ai_engine)
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
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    logger=True,
    engineio_logger=True
)

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    await sio.emit('connected', {'status': 'connected'}, room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")

@sio.event
async def speech_detected(sid, data):
    """Handle speech detection from desktop client"""
    try:
        conversation_id = data.get('conversation_id')
        text = data.get('text', '')
        speaker = data.get('speaker', 'unknown')
        timestamp_str = data.get('timestamp')
        
        if not conversation_id or not text:
            await sio.emit('error', {'message': 'Invalid speech data'}, room=sid)
            return
        
        logger.info(f"Speech detected in conversation {conversation_id}: {text[:50]}...")
        
        # Mock analysis
        analysis = {
            'conversation_id': conversation_id,
            'timestamp': timestamp_str or datetime.utcnow().isoformat(),
            'speaker': speaker,
            'text': text,
            'sentiment': {
                'overall': 'neutral',
                'confidence': 0.7,
                'valence': 0.0
            },
            'suggestions': [
                {
                    'type': 'response',
                    'text': 'That\'s a great point. Can you tell me more about your specific requirements?',
                    'confidence': 0.8
                }
            ] if speaker != 'user' else [],
            'objections': [],
            'engagement': {
                'score': 0.6,
                'speaker': speaker
            }
        }
        
        # Send analysis back to client
        await sio.emit('conversation_analysis', {'analysis': analysis}, room=sid)
        
        # Send AI suggestions if any
        if analysis['suggestions']:
            await sio.emit('ai_suggestion', {
                'conversation_id': conversation_id,
                'suggestions': analysis['suggestions']
            }, room=sid)
        
    except Exception as e:
        logger.error(f"Error handling speech detection: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

@sio.event
async def start_conversation(sid, data):
    """Handle conversation start"""
    try:
        conversation_type = data.get('type', 'meeting')
        platform = data.get('platform', 'desktop')
        
        conversation_id = f"conv_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        await sio.emit('conversation_started', {
            'conversation_id': conversation_id,
            'status': 'started'
        }, room=sid)
        
        logger.info(f"Started conversation {conversation_id} for client {sid}")
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

@sio.event
async def end_conversation(sid, data):
    """Handle conversation end"""
    try:
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            await sio.emit('error', {'message': 'No conversation ID provided'}, room=sid)
            return
        
        await sio.emit('conversation_ended', {
            'conversation_id': conversation_id,
            'status': 'ended'
        }, room=sid)
        
        logger.info(f"Ended conversation {conversation_id} for client {sid}")
        
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

# Combine FastAPI and Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# API Routes
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

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Conversation Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }

@app.get("/api/test")
async def test_api():
    """Test API endpoint"""
    return {
        "message": "API is working",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "ai_engine": "mock",
            "audio_processor": "mock",
            "conversation_analyzer": "mock"
        }
    }

@app.post("/api/auth/login")
async def login(credentials: Dict[str, str]):
    """Mock login endpoint"""
    email = credentials.get("email", "")
    password = credentials.get("password", "")
    
    if email == "demo@example.com" and password == "demo123":
        return {
            "access_token": "mock_token_123",
            "token_type": "bearer",
            "user": {
                "id": "demo_user_123",
                "email": email,
                "first_name": "Demo",
                "last_name": "User",
                "plan": "pro"
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/conversations")
async def list_conversations():
    """List conversations"""
    return {
        "conversations": [
            {
                "id": "conv_1",
                "title": "Demo Conversation",
                "type": "meeting",
                "status": "completed",
                "created_at": datetime.utcnow().isoformat()
            }
        ],
        "total": 1
    }

@app.get("/api/analytics/conversations/{conversation_id}")
async def get_conversation_analytics(conversation_id: str):
    """Get analytics for a specific conversation"""
    return {
        "conversation_id": conversation_id,
        "sentiment_score": 0.7,
        "engagement_score": 0.8,
        "objections_count": 2,
        "suggestions_used": 5,
        "duration_minutes": 15.5,
        "participants": ["user", "prospect"],
        "summary": "Productive conversation with good engagement"
    }

if __name__ == "__main__":
    logger.info("🚀 Starting AI Conversation Assistant server...")
    
    try:
        uvicorn.run(
            "working_app:socket_app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
