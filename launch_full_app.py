#!/usr/bin/env python3
"""
Complete AI Conversation Assistant Launcher
Starts all components: Backend, Frontend, and Desktop App
"""

import subprocess
import time
import webbrowser
import sys
import os
from pathlib import Path
import threading
import requests

class AppLauncher:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        
    def log(self, message):
        """Print formatted log message"""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def check_port(self, port):
        """Check if a port is available"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def wait_for_service(self, url, timeout=30):
        """Wait for a service to become available"""
        self.log(f"⏳ Waiting for service at {url}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    self.log(f"✅ Service at {url} is ready!")
                    return True
            except:
                pass
            time.sleep(1)
        
        self.log(f"❌ Service at {url} failed to start within {timeout} seconds")
        return False
    
    def start_backend(self):
        """Start the Python backend"""
        self.log("🚀 Starting Python Backend...")
        
        if not self.check_port(8000):
            self.log("⚠️  Port 8000 is already in use, backend might already be running")
            return True
        
        try:
            # Start the working app (stable version)
            process = subprocess.Popen([
                sys.executable, "working_app.py"
            ], cwd=self.base_dir)
            
            self.processes.append(("Backend", process))
            
            # Wait for backend to be ready
            if self.wait_for_service("http://localhost:8000/health"):
                self.log("✅ Backend started successfully!")
                return True
            else:
                self.log("❌ Backend failed to start")
                return False
                
        except Exception as e:
            self.log(f"❌ Error starting backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend server"""
        self.log("🌐 Starting Frontend Server...")
        
        if not self.check_port(3000):
            self.log("⚠️  Port 3000 is already in use, frontend might already be running")
            return True
        
        try:
            process = subprocess.Popen([
                sys.executable, "serve_frontend.py"
            ], cwd=self.base_dir)
            
            self.processes.append(("Frontend", process))
            
            # Wait for frontend to be ready
            if self.wait_for_service("http://localhost:3000", timeout=10):
                self.log("✅ Frontend started successfully!")
                return True
            else:
                self.log("❌ Frontend failed to start")
                return False
                
        except Exception as e:
            self.log(f"❌ Error starting frontend: {e}")
            return False
    
    def start_desktop_app(self):
        """Start the desktop application"""
        self.log("🖥️  Starting Desktop Application...")
        
        try:
            desktop_dir = self.base_dir / "desktop"
            if not desktop_dir.exists():
                self.log("⚠️  Desktop directory not found, skipping desktop app")
                return True
            
            process = subprocess.Popen([
                sys.executable, "main.py"
            ], cwd=desktop_dir)
            
            self.processes.append(("Desktop", process))
            self.log("✅ Desktop application started!")
            return True
            
        except Exception as e:
            self.log(f"❌ Error starting desktop app: {e}")
            return False
    
    def open_browser(self):
        """Open browser to the frontend"""
        self.log("🌐 Opening browser...")
        time.sleep(3)  # Give frontend time to start
        try:
            webbrowser.open("http://localhost:3000")
            self.log("✅ Browser opened!")
        except Exception as e:
            self.log(f"❌ Error opening browser: {e}")
    
    def show_status(self):
        """Show application status"""
        self.log("\n" + "="*60)
        self.log("🎉 AI CONVERSATION ASSISTANT - FULLY LAUNCHED!")
        self.log("="*60)
        self.log("📊 Application Status:")
        self.log("   • Backend API:     http://localhost:8000")
        self.log("   • Frontend Web:    http://localhost:3000")
        self.log("   • API Docs:        http://localhost:8000/docs")
        self.log("   • Health Check:    http://localhost:8000/health")
        self.log("")
        self.log("🔧 Available Features:")
        self.log("   • Real-time conversation analysis")
        self.log("   • AI-powered suggestions")
        self.log("   • Speech recognition")
        self.log("   • Analytics dashboard")
        self.log("   • Socket.IO real-time communication")
        self.log("")
        self.log("💡 Usage Instructions:")
        self.log("   1. Open http://localhost:3000 in your browser")
        self.log("   2. Click 'Start Conversation' to begin")
        self.log("   3. Type messages or use voice input")
        self.log("   4. Get real-time AI suggestions and analysis")
        self.log("")
        self.log("🛑 To stop all services, press Ctrl+C")
        self.log("="*60)
    
    def cleanup(self):
        """Clean up running processes"""
        self.log("\n🛑 Shutting down all services...")
        
        for name, process in self.processes:
            try:
                self.log(f"   Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                self.log(f"   ✅ {name} stopped")
            except subprocess.TimeoutExpired:
                self.log(f"   ⚠️  {name} didn't stop gracefully, forcing...")
                process.kill()
            except Exception as e:
                self.log(f"   ❌ Error stopping {name}: {e}")
        
        self.log("✅ All services stopped")
    
    def launch(self):
        """Launch the complete application"""
        self.log("🚀 Starting AI Conversation Assistant...")
        self.log("="*50)
        
        try:
            # Start backend
            if not self.start_backend():
                self.log("❌ Failed to start backend, aborting")
                return False
            
            # Start frontend
            if not self.start_frontend():
                self.log("❌ Failed to start frontend, aborting")
                return False
            
            # Start desktop app (optional)
            self.start_desktop_app()
            
            # Open browser
            browser_thread = threading.Thread(target=self.open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Show status
            self.show_status()
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
            return True
            
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main launcher function"""
    launcher = AppLauncher()
    success = launcher.launch()
    
    if success:
        print("\n🎉 Application launched successfully!")
    else:
        print("\n❌ Application failed to launch")
        sys.exit(1)

if __name__ == "__main__":
    main()
