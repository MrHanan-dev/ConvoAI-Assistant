#!/usr/bin/env python3
"""
Start AI Conversation Assistant with Cohere API key
"""

import os
import subprocess
import sys

def main():
    """Start the application with Cohere API key"""
    print("🚀 Starting AI Conversation Assistant with Cohere...")
    
    # Set the Cohere API key
    api_key = "NHlCa1jrvthkgsJZk4RJoSFXdF1HxE6mUe8YXdmx"
    os.environ['COHERE_API_KEY'] = api_key
    
    print(f"✅ Cohere API key set: {api_key[:10]}...")
    print("🤖 Starting application...")
    
    # Start the application
    try:
        subprocess.run([sys.executable, "working_app_with_cohere.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    main()
