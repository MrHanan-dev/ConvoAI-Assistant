#!/usr/bin/env python3
"""
Cohere API Key Setup Script
Helps you configure Cohere for AI responses
"""

import os
import sys
from pathlib import Path

def setup_cohere_api_key():
    """Interactive setup for Cohere API key"""
    print("🤖 Cohere AI Integration Setup")
    print("=" * 50)
    
    # Check if API key is already set
    current_key = os.getenv('COHERE_API_KEY')
    if current_key and current_key != 'your-cohere-api-key-here':
        print(f"✅ Cohere API key is already set: {current_key[:10]}...")
        choice = input("Do you want to update it? (y/n): ").lower()
        if choice != 'y':
            print("Keeping existing API key.")
            return current_key
    
    print("\n📋 To get your Cohere API key:")
    print("1. Go to https://cohere.ai/")
    print("2. Sign up for a free account")
    print("3. Go to your dashboard")
    print("4. Copy your API key")
    print()
    
    api_key = input("Enter your Cohere API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Skipping setup.")
        return None
    
    if api_key == 'your-cohere-api-key-here':
        print("❌ Please enter a real API key, not the placeholder.")
        return None
    
    # Test the API key
    print("\n🧪 Testing API key...")
    try:
        import cohere
        client = cohere.Client(api_key)
        
        # Test with a simple request
        response = client.generate(
            prompt="Hello",
            model="command",
            max_tokens=10,
            temperature=0.7
        )
        
        print("✅ API key is valid!")
        print(f"Test response: {response.generations[0].text.strip()}")
        
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        choice = input("Do you want to continue anyway? (y/n): ").lower()
        if choice != 'y':
            return None
    
    # Set the environment variable for current session
    os.environ['COHERE_API_KEY'] = api_key
    print(f"\n✅ API key set for current session: {api_key[:10]}...")
    
    # Create .env file
    env_file = Path('.env')
    env_content = f"COHERE_API_KEY={api_key}\n"
    
    if env_file.exists():
        # Read existing content
        with open(env_file, 'r') as f:
            existing_content = f.read()
        
        # Update or add COHERE_API_KEY
        lines = existing_content.split('\n')
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('COHERE_API_KEY='):
                lines[i] = f"COHERE_API_KEY={api_key}"
                updated = True
                break
        
        if not updated:
            lines.append(f"COHERE_API_KEY={api_key}")
        
        env_content = '\n'.join(lines)
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ API key saved to .env file")
    
    return api_key

def main():
    """Main setup function"""
    try:
        api_key = setup_cohere_api_key()
        
        if api_key:
            print("\n🎉 Setup Complete!")
            print("=" * 50)
            print("✅ Cohere API key configured")
            print("✅ Environment variable set")
            print("✅ .env file updated")
            print()
            print("🚀 Next steps:")
            print("1. Restart the application: python working_app_with_cohere.py")
            print("2. Open http://localhost:3000 in your browser")
            print("3. Start chatting with AI-powered responses!")
            print()
            print("💡 Your AI responses will now be powered by Cohere!")
        else:
            print("\n⚠️ Setup incomplete. You can run this script again anytime.")
            print("The application will work with fallback responses until you set up Cohere.")
    
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")

if __name__ == "__main__":
    main()
