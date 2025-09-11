#!/usr/bin/env python3
"""
AI Conversation Assistant - Application Launcher
Starts the Python-based AI conversation assistant with all components
"""

import sys
import os
import subprocess
import asyncio
import time
import signal
from pathlib import Path
from loguru import logger
import multiprocessing as mp


def setup_logging():
    """Set up logging configuration"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add("logs/launcher.log", rotation="5 MB", retention="3 days")


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    logger.info(f"Python version: {sys.version}")
    return True


def install_dependencies():
    """Install required dependencies"""
    try:
        logger.info("Checking and installing dependencies...")
        
        # Install main requirements
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        
        # Install desktop requirements
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "desktop/requirements.txt"
        ])
        
        logger.success("Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False


def check_environment():
    """Check environment variables and configuration"""
    try:
        # Check for .env file
        env_file = Path(".env")
        if not env_file.exists():
            logger.warning(".env file not found. Using example configuration.")
            
            # Copy example env file
            example_env = Path("env.example")
            if example_env.exists():
                import shutil
                shutil.copy(example_env, env_file)
                logger.info("Created .env file from example")
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check critical environment variables
        required_vars = ["OPENAI_API_KEY", "DATABASE_URL"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
            logger.info("Please update your .env file with the required values")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking environment: {e}")
        return False


def start_backend_server():
    """Start the FastAPI backend server"""
    try:
        logger.info("Starting backend server...")
        
        # Start the main FastAPI server
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], cwd=".", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            logger.success("Backend server started successfully!")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"Backend server failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        logger.error(f"Error starting backend server: {e}")
        return None


def start_desktop_app():
    """Start the desktop application"""
    try:
        logger.info("Starting desktop application...")
        
        # Start the desktop app
        process = subprocess.Popen([
            sys.executable, "desktop/main.py"
        ], cwd=".")
        
        return process
        
    except Exception as e:
        logger.error(f"Error starting desktop app: {e}")
        return None


def start_web_dashboard():
    """Start the web dashboard (if available)"""
    try:
        dashboard_dir = Path("frontend")
        if not dashboard_dir.exists():
            logger.info("Web dashboard not available (frontend directory not found)")
            return None
        
        logger.info("Starting web dashboard...")
        
        # Check if npm is available
        try:
            subprocess.check_call(["npm", "--version"], stdout=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("npm not found. Web dashboard will not be started.")
            return None
        
        # Install dependencies and start
        subprocess.check_call(["npm", "install"], cwd="frontend")
        process = subprocess.Popen(["npm", "start"], cwd="frontend")
        
        logger.success("Web dashboard started!")
        return process
        
    except Exception as e:
        logger.error(f"Error starting web dashboard: {e}")
        return None


def main():
    """Main launcher function"""
    setup_logging()
    
    logger.info("🚀 Starting AI Conversation Assistant...")
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    
    # Check environment
    if not check_environment():
        logger.warning("Environment check failed, but continuing...")
    
    # Install dependencies
    if not install_dependencies():
        logger.error("Failed to install dependencies")
        sys.exit(1)
    
    # Start components
    processes = []
    
    try:
        # Start backend server
        backend_process = start_backend_server()
        if backend_process:
            processes.append(("Backend Server", backend_process))
        else:
            logger.error("Failed to start backend server")
            sys.exit(1)
        
        # Start web dashboard (optional)
        dashboard_process = start_web_dashboard()
        if dashboard_process:
            processes.append(("Web Dashboard", dashboard_process))
        
        # Start desktop app
        desktop_process = start_desktop_app()
        if desktop_process:
            processes.append(("Desktop App", desktop_process))
        else:
            logger.error("Failed to start desktop application")
            # Don't exit, backend might still be useful
        
        logger.success("🎉 AI Conversation Assistant started successfully!")
        logger.info("Running components:")
        for name, process in processes:
            logger.info(f"  - {name} (PID: {process.pid})")
        
        logger.info("\nPress Ctrl+C to stop all components")
        
        # Wait for processes and handle shutdown
        def signal_handler(signum, frame):
            logger.info("\n🛑 Shutting down AI Conversation Assistant...")
            for name, process in processes:
                try:
                    logger.info(f"Stopping {name}...")
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing {name}...")
                    process.kill()
                except Exception as e:
                    logger.error(f"Error stopping {name}: {e}")
            
            logger.success("✅ All components stopped")
            sys.exit(0)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep the launcher running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            for name, process in processes[:]:
                if process.poll() is not None:
                    logger.warning(f"{name} has stopped unexpectedly")
                    processes.remove((name, process))
            
            # If all critical processes stopped, exit
            if not any(name == "Backend Server" for name, _ in processes):
                logger.error("Backend server stopped. Shutting down.")
                break
    
    except KeyboardInterrupt:
        logger.info("\n🛑 Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Cleanup
        for name, process in processes:
            try:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=3)
            except:
                pass
        
        logger.info("✅ Launcher shutdown complete")


if __name__ == "__main__":
    main()
