#!/usr/bin/env python3
"""
Minimal test to check if basic components work
"""

import sys
import asyncio
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO")

async def test_basic_components():
    """Test basic components without heavy dependencies"""
    try:
        logger.info("Testing basic components...")
        
        # Test 1: Config
        logger.info("1. Testing config...")
        from app.core.config import settings
        logger.success(f"   ✓ Config loaded: {settings.APP_NAME}")
        
        # Test 2: Database (without actual connection)
        logger.info("2. Testing database module...")
        from app.core.database import Base
        logger.success("   ✓ Database module loaded")
        
        # Test 3: Redis (without actual connection)
        logger.info("3. Testing Redis module...")
        from app.core.redis_client import redis_client
        logger.success("   ✓ Redis module loaded")
        
        # Test 4: API routes
        logger.info("4. Testing API routes...")
        from app.api.api_routes import api_router
        logger.success("   ✓ API routes loaded")
        
        # Test 5: Socket handlers
        logger.info("5. Testing socket handlers...")
        from app.sockets.handlers import register_socket_handlers
        logger.success("   ✓ Socket handlers loaded")
        
        logger.success("✅ All basic components loaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ai_components():
    """Test AI components (these might fail due to missing dependencies)"""
    try:
        logger.info("Testing AI components...")
        
        # Test AI Engine (this might fail due to heavy dependencies)
        logger.info("1. Testing AI Engine...")
        try:
            from app.services.ai_engine import AIEngine
            logger.success("   ✓ AI Engine module loaded")
        except Exception as e:
            logger.warning(f"   ⚠ AI Engine failed: {e}")
        
        # Test Audio Processor (this might fail due to audio dependencies)
        logger.info("2. Testing Audio Processor...")
        try:
            from app.services.audio_processor import AudioProcessor
            logger.success("   ✓ Audio Processor module loaded")
        except Exception as e:
            logger.warning(f"   ⚠ Audio Processor failed: {e}")
        
        # Test Conversation Analyzer
        logger.info("3. Testing Conversation Analyzer...")
        try:
            from app.services.conversation_analyzer import ConversationAnalyzer
            logger.success("   ✓ Conversation Analyzer module loaded")
        except Exception as e:
            logger.warning(f"   ⚠ Conversation Analyzer failed: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ AI component test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Starting minimal component test...")
    logger.info("=" * 50)
    
    # Test basic components
    basic_success = await test_basic_components()
    
    if basic_success:
        # Test AI components
        await test_ai_components()
    
    logger.info("=" * 50)
    logger.info("Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
