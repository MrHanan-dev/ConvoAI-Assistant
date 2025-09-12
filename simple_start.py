#!/usr/bin/env python3
"""
Simple startup script for the AI Conversation Assistant
This version starts with minimal dependencies and adds features gradually
"""

import sys
import asyncio
from loguru import logger
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO")

# Create a simple FastAPI app
app = FastAPI(
    title="AI Conversation Assistant",
    description="Real-time AI-powered conversation assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Conversation Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "message": "Test endpoint working",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    logger.info("🚀 Starting AI Conversation Assistant (Simple Mode)...")
    logger.info("This is a minimal version for testing")
    
    try:
        uvicorn.run(
            "simple_start:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
