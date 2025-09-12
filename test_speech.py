#!/usr/bin/env python3
"""
Test Speech Recognition Functionality
"""

import asyncio
import requests
import json
import time

def test_microphone():
    """Test microphone functionality"""
    print("🎤 Testing microphone...")
    try:
        response = requests.get("http://localhost:8000/api/speech/test")
        result = response.json()
        
        if result["success"]:
            print("✅ Microphone test passed!")
            print(f"   Message: {result['message']}")
        else:
            print("❌ Microphone test failed!")
            print(f"   Message: {result['message']}")
        
        return result["success"]
    except Exception as e:
        print(f"❌ Error testing microphone: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition"""
    print("\n🎤 Testing speech recognition...")
    print("   Please speak clearly into your microphone...")
    print("   (You have 10 seconds to speak)")
    
    try:
        response = requests.post("http://localhost:8000/api/speech/listen", timeout=20)
        result = response.json()
        
        if result["success"]:
            print("✅ Speech recognition successful!")
            print(f"   Transcribed text: '{result['text']}'")
            return result["text"]
        else:
            print("❌ Speech recognition failed!")
            print(f"   Message: {result['message']}")
            return None
            
    except Exception as e:
        print(f"❌ Error in speech recognition: {e}")
        return None

def test_speech_chat():
    """Test speech-to-AI chat"""
    print("\n🤖 Testing speech-to-AI chat...")
    print("   Please speak a question or message...")
    print("   (You have 10 seconds to speak)")
    
    try:
        response = requests.post("http://localhost:8000/api/speech/chat", timeout=25)
        result = response.json()
        
        if result["success"]:
            print("✅ Speech-to-AI chat successful!")
            print(f"   You said: '{result['transcribed_text']}'")
            print(f"   AI responded: '{result['ai_response']}'")
            return True
        else:
            print("❌ Speech-to-AI chat failed!")
            print(f"   Message: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error in speech-to-AI chat: {e}")
        return False

def main():
    """Main test function"""
    print("🎤 Speech Recognition Test Suite")
    print("=" * 50)
    
    # Test 1: Microphone test
    mic_ok = test_microphone()
    
    if not mic_ok:
        print("\n❌ Microphone test failed. Please check your microphone and try again.")
        return
    
    # Test 2: Speech recognition
    transcribed = test_speech_recognition()
    
    if not transcribed:
        print("\n❌ Speech recognition failed. Please try again.")
        return
    
    # Test 3: Speech-to-AI chat
    chat_ok = test_speech_chat()
    
    if chat_ok:
        print("\n🎉 All speech recognition tests passed!")
        print("✅ Your AI Conversation Assistant can now understand speech!")
    else:
        print("\n⚠️ Speech recognition works, but AI chat failed.")
        print("   Check if the AI engine is working properly.")

if __name__ == "__main__":
    main()
