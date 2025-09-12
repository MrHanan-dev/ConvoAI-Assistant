#!/usr/bin/env python3
"""
Startup script for AI Conversation Assistant
This script handles missing dependencies gracefully and provides fallbacks
"""

import sys
import os
import asyncio
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO")

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    # Check core dependencies
    try:
        import fastapi
        logger.info("✓ FastAPI available")
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import uvicorn
        logger.info("✓ Uvicorn available")
    except ImportError:
        missing_deps.append("uvicorn")
    
    try:
        import socketio
        logger.info("✓ SocketIO available")
    except ImportError:
        missing_deps.append("python-socketio")
    
    # Check optional dependencies
    optional_deps = []
    
    try:
        import openai
        logger.info("✓ OpenAI available")
    except ImportError:
        optional_deps.append("openai")
    
    try:
        import transformers
        logger.info("✓ Transformers available")
    except ImportError:
        optional_deps.append("transformers")
    
    try:
        import pyaudio
        logger.info("✓ PyAudio available")
    except ImportError:
        optional_deps.append("pyaudio")
    
    try:
        import redis
        logger.info("✓ Redis available")
    except ImportError:
        optional_deps.append("redis")
    
    return missing_deps, optional_deps

def install_dependencies(deps):
    """Install missing dependencies"""
    if not deps:
        return True
    
    logger.info(f"Installing missing dependencies: {', '.join(deps)}")
    
    try:
        import subprocess
        for dep in deps:
            logger.info(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        return True
    except Exception as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

async def start_application():
    """Start the application with appropriate fallbacks"""
    logger.info("🚀 Starting AI Conversation Assistant...")
    
    # Check dependencies
    missing_deps, optional_deps = check_dependencies()
    
    if missing_deps:
        logger.warning(f"Missing required dependencies: {', '.join(missing_deps)}")
        logger.info("Attempting to install missing dependencies...")
        
        if not install_dependencies(missing_deps):
            logger.error("Failed to install required dependencies. Please install them manually:")
            for dep in missing_deps:
                logger.error(f"  pip install {dep}")
            return False
    
    if optional_deps:
        logger.warning(f"Missing optional dependencies: {', '.join(optional_deps)}")
        logger.info("Some features may not be available")
    
    # Try to start the working application
    try:
        logger.info("Starting application...")
        
        # Import and run the working app
        from working_app import socket_app
        import uvicorn
        
        await uvicorn.Server(
            uvicorn.Config(
                app=socket_app,
                host="0.0.0.0",
                port=8000,
                log_level="info"
            )
        ).serve()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.info("Falling back to simple mode...")
        
        # Fallback to simple mode
        try:
            from simple_start import app
            import uvicorn
            
            await uvicorn.Server(
                uvicorn.Config(
                    app=app,
                    host="0.0.0.0",
                    port=8000,
                    log_level="info"
                )
            ).serve()
            
        except Exception as e2:
            logger.error(f"Failed to start simple mode: {e2}")
            return False
    
    return True

def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("AI Conversation Assistant - Startup Script")
    logger.info("=" * 60)
    
    try:
        # Create necessary directories
        os.makedirs("logs", exist_ok=True)
        
        # Start the application
        success = asyncio.run(start_application())
        
        if success:
            logger.info("✅ Application started successfully!")
        else:
            logger.error("❌ Failed to start application")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
