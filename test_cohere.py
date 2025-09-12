#!/usr/bin/env python3
"""
Test Cohere API connection
"""

import os
import cohere

def test_cohere():
    """Test Cohere API connection"""
    print("🧪 Testing Cohere API Connection")
    print("=" * 40)
    
    # Check environment variable
    api_key = os.getenv('COHERE_API_KEY')
    print(f"API Key: {api_key[:10] if api_key else 'None'}...")
    
    if not api_key:
        print("❌ No API key found in environment")
        return False
    
    try:
        # Initialize client
        client = cohere.Client(api_key)
        print("✅ Cohere client initialized")
        
        # Test Chat API
        print("\n🔬 Testing Chat API...")
        try:
            response = client.chat(
                message="Hello, how are you?",
                model="command-r-plus",
                max_tokens=50,
                temperature=0.7
            )
            print(f"✅ Chat API Response: {response.text}")
            return True
        except Exception as e:
            print(f"❌ Chat API failed: {e}")
            
            # Try Generate API as fallback
            print("\n🔬 Testing Generate API...")
            try:
                response = client.generate(
                    prompt="Hello, how are you?",
                    model="command",
                    max_tokens=50,
                    temperature=0.7
                )
                print(f"✅ Generate API Response: {response.generations[0].text}")
                return True
            except Exception as e2:
                print(f"❌ Generate API failed: {e2}")
                return False
                
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = test_cohere()
    if success:
        print("\n🎉 Cohere API is working!")
    else:
        print("\n❌ Cohere API test failed")
