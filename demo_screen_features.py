#!/usr/bin/env python3
"""
Demo Script for Real-time Screen Analysis Features
"""
import requests
import json
import time

def test_screen_features():
    """Test all screen capture features"""
    base_url = "http://localhost:8000"
    
    print("🎥 Real-time Screen Analysis Demo")
    print("=" * 50)
    
    # 1. Check screen status
    print("\n1. Checking screen capture status...")
    try:
        response = requests.get(f"{base_url}/api/screen/status")
        data = response.json()
        print(f"✅ Status: {data['message']}")
        print(f"   Available: {data['available']}")
        print(f"   Capturing: {data['is_capturing']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 2. Start screen capture
    print("\n2. Starting screen capture...")
    try:
        response = requests.post(f"{base_url}/api/screen/start")
        data = response.json()
        if data['success']:
            print("✅ Screen capture started successfully")
        else:
            print(f"❌ Failed: {data['message']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 3. Wait for capture to process
    print("\n3. Waiting for screen analysis...")
    time.sleep(3)
    
    # 4. Test screen chat with AI
    print("\n4. Testing AI screen analysis...")
    questions = [
        "What do you see on my screen?",
        "Are there any buttons visible?",
        "What's the activity level on my screen?",
        "Can you describe the UI elements?"
    ]
    
    for question in questions:
        print(f"\n   Question: {question}")
        try:
            response = requests.post(
                f"{base_url}/api/screen/chat",
                json={"message": question}
            )
            data = response.json()
            
            if data['success']:
                print(f"   AI Response: {data['ai_response']}")
                print(f"   Screen Context: {data['screen_summary']}")
            else:
                print(f"   ❌ Failed: {data['message']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)
    
    # 5. Test regular chat with screen context
    print("\n5. Testing regular chat with screen context...")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={"message": "Help me understand what's happening on my screen"}
        )
        data = response.json()
        print(f"✅ Chat Response: {data['response']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 6. Stop screen capture
    print("\n6. Stopping screen capture...")
    try:
        response = requests.post(f"{base_url}/api/screen/stop")
        data = response.json()
        if data['success']:
            print("✅ Screen capture stopped successfully")
        else:
            print(f"❌ Failed: {data['message']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Demo completed!")
    print("\nFeatures demonstrated:")
    print("✅ Real-time screen capture")
    print("✅ Computer vision analysis")
    print("✅ AI-powered screen understanding")
    print("✅ Context-aware responses")
    print("✅ UI element detection")
    print("✅ Activity level monitoring")

if __name__ == "__main__":
    test_screen_features()
