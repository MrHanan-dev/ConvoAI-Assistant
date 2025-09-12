#!/usr/bin/env python3
"""
Test script to check application components
"""

import sys
import traceback

def test_imports():
    """Test importing all modules"""
    try:
        print("Testing imports...")
        
        print("1. Testing config...")
        from app.core.config import settings
        print("   ✓ Config loaded successfully")
        
        print("2. Testing database...")
        from app.core.database import init_db
        print("   ✓ Database module loaded")
        
        print("3. Testing Redis...")
        from app.core.redis_client import init_redis
        print("   ✓ Redis module loaded")
        
        print("4. Testing API routes...")
        from app.api.api_routes import api_router
        print("   ✓ API routes loaded")
        
        print("5. Testing AI Engine...")
        from app.services.ai_engine import AIEngine
        print("   ✓ AI Engine loaded")
        
        print("6. Testing Audio Processor...")
        from app.services.audio_processor import AudioProcessor
        print("   ✓ Audio Processor loaded")
        
        print("7. Testing Conversation Analyzer...")
        from app.services.conversation_analyzer import ConversationAnalyzer
        print("   ✓ Conversation Analyzer loaded")
        
        print("8. Testing Socket handlers...")
        from app.sockets.handlers import register_socket_handlers
        print("   ✓ Socket handlers loaded")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality"""
    try:
        print("\nTesting basic functionality...")
        
        from app.core.config import settings
        print(f"   App name: {settings.APP_NAME}")
        print(f"   Debug mode: {settings.DEBUG}")
        print(f"   Host: {settings.HOST}")
        print(f"   Port: {settings.PORT}")
        
        print("✅ Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing AI Conversation Assistant...")
    print("=" * 50)
    
    if test_imports():
        test_basic_functionality()
    
    print("\n" + "=" * 50)
    print("Test completed!")
