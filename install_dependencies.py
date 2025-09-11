#!/usr/bin/env python3
"""
Dependency Installation Script for AI Conversation Assistant
Installs all required packages for Cluely.ai functionality
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package):
    """Install a single package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Install all dependencies"""
    print("🚀 Installing AI Conversation Assistant Dependencies...")
    print("📦 This will install all packages needed for Cluely.ai functionality")
    
    # Core dependencies for basic functionality
    core_packages = [
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0", 
        "python-socketio>=5.10.0",
        "sqlalchemy>=2.0.23",
        "redis>=5.0.1",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "cryptography>=41.0.8",
        "openai>=1.3.8",
        "numpy>=1.24.4",
        "loguru>=0.7.2",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.2",
        "aiofiles>=23.2.1",
        "requests>=2.31.0",
        "aiohttp>=3.9.1"
    ]
    
    # AI and ML packages
    ai_packages = [
        "transformers>=4.36.2",
        "sentence-transformers>=2.2.2",
        "torch>=2.1.2",
        "scikit-learn>=1.3.2",
        "whisper>=1.1.10"
    ]
    
    # Audio processing packages  
    audio_packages = [
        "pyaudio>=0.2.11",
        "librosa>=0.10.1",
        "sounddevice>=0.4.6",
        "pydub>=0.25.1",
        "speech-recognition>=3.10.0",
        "webrtcvad>=2.0.10"
    ]
    
    # Desktop GUI packages
    gui_packages = [
        "customtkinter>=5.2.2",
        "pillow>=10.1.0",
        "pystray>=0.19.4"
    ]
    
    # System integration packages
    system_packages = [
        "psutil>=5.9.6",
        "keyboard>=0.13.5",
        "mouse>=0.7.1"
    ]
    
    # Vector database packages
    vector_packages = [
        "chromadb>=0.4.18",
        "pinecone-client>=2.2.4"
    ]
    
    all_package_groups = [
        ("Core Packages", core_packages),
        ("AI/ML Packages", ai_packages),
        ("Audio Processing", audio_packages),
        ("Desktop GUI", gui_packages),
        ("System Integration", system_packages),
        ("Vector Database", vector_packages)
    ]
    
    total_installed = 0
    total_failed = 0
    
    for group_name, packages in all_package_groups:
        print(f"\n📦 Installing {group_name}...")
        
        for package in packages:
            package_name = package.split(">=")[0].split("==")[0]
            print(f"  Installing {package_name}...", end=" ")
            
            if install_package(package):
                print("✅")
                total_installed += 1
            else:
                print("❌")
                total_failed += 1
                print(f"    ⚠️ Failed to install {package_name}")
    
    print(f"\n📊 Installation Summary:")
    print(f"  ✅ Successfully installed: {total_installed}")
    print(f"  ❌ Failed to install: {total_failed}")
    print(f"  📈 Success rate: {(total_installed/(total_installed+total_failed)*100):.1f}%")
    
    if total_failed == 0:
        print("\n🎉 ALL DEPENDENCIES INSTALLED SUCCESSFULLY!")
        print("✅ Your Cluely.ai clone is ready to run!")
        print("\n🚀 Start the application:")
        print("   python start_python_app.py")
        print("   OR")
        print("   start_app.bat")
    else:
        print(f"\n⚠️ {total_failed} packages failed to install.")
        print("💡 The application may still work with reduced functionality.")
        print("🔧 You can manually install missing packages later.")
    
    print("\n📄 See requirements.txt for complete package list")

if __name__ == "__main__":
    main()
