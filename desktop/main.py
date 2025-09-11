"""
AI Conversation Assistant - Desktop Application
Real-time conversation overlay with AI suggestions
"""

import sys
import asyncio
import json
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw
import socketio
import requests
from loguru import logger

from services.audio_manager import AudioManager
from services.api_client import APIClient
from ui.overlay_window import OverlayWindow
from ui.settings_window import SettingsWindow
from ui.dashboard_window import DashboardWindow
from config.settings import DesktopSettings


class AIConversationAssistant:
    """Main desktop application class"""
    
    def __init__(self):
        # Initialize settings
        self.settings = DesktopSettings()
        
        # Initialize services
        self.audio_manager = None
        self.api_client = None
        self.socket_client = None
        
        # UI components
        self.overlay_window = None
        self.settings_window = None
        self.dashboard_window = None
        self.system_tray = None
        
        # Application state
        self.is_running = False
        self.is_recording = False
        self.current_conversation_id = None
        self.conversation_data = []
        self.suggestions_queue = []
        
        # Threading
        self.main_thread = None
        self.audio_thread = None
        
        # Configure logging
        logger.add("logs/desktop.log", rotation="10 MB", retention="5 days")
        
    async def initialize(self):
        """Initialize all components"""
        try:
            logger.info("Initializing AI Conversation Assistant...")
            
            # Initialize API client
            self.api_client = APIClient(
                base_url=self.settings.API_BASE_URL,
                api_key=self.settings.API_KEY
            )
            
            # Test API connection
            if not await self.api_client.test_connection():
                logger.error("Failed to connect to API server")
                messagebox.showerror("Connection Error", "Cannot connect to AI server. Please check your settings.")
                return False
            
            # Initialize Socket.IO client
            self.socket_client = socketio.AsyncClient()
            await self._setup_socket_handlers()
            
            # Connect to server
            await self.socket_client.connect(self.settings.API_BASE_URL)
            logger.info("Connected to AI server")
            
            # Initialize audio manager
            self.audio_manager = AudioManager()
            await self.audio_manager.initialize()
            
            # Set up audio callback
            self.audio_manager.set_transcription_callback(self._on_speech_detected)
            
            # Initialize UI components
            self._initialize_ui()
            
            # Create system tray
            self._create_system_tray()
            
            self.is_running = True
            logger.success("AI Conversation Assistant initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            messagebox.showerror("Initialization Error", f"Failed to start application: {e}")
            return False
    
    def _initialize_ui(self):
        """Initialize UI components"""
        # Set theme
        ctk.set_appearance_mode(self.settings.THEME)
        ctk.set_default_color_theme(self.settings.COLOR_THEME)
        
        # Create overlay window
        self.overlay_window = OverlayWindow(
            settings=self.settings,
            on_suggestion_click=self._on_suggestion_click,
            on_toggle_recording=self._toggle_recording,
            on_open_settings=self._open_settings,
            on_open_dashboard=self._open_dashboard
        )
        
        # Create settings window (hidden initially)
        self.settings_window = SettingsWindow(
            settings=self.settings,
            on_settings_changed=self._on_settings_changed,
            on_test_audio=self._test_audio_devices
        )
        
        # Create dashboard window (hidden initially)
        self.dashboard_window = DashboardWindow(
            api_client=self.api_client,
            on_conversation_selected=self._on_conversation_selected
        )
    
    def _create_system_tray(self):
        """Create system tray icon"""
        try:
            # Create icon image
            image = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(image)
            draw.rectangle([16, 16, 48, 48], fill='white')
            draw.text((20, 25), "AI", fill='blue')
            
            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem("Show Overlay", self._show_overlay),
                pystray.MenuItem("Settings", self._open_settings),
                pystray.MenuItem("Dashboard", self._open_dashboard),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Start Recording", self._toggle_recording),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", self._quit_application)
            )
            
            # Create tray icon
            self.system_tray = pystray.Icon(
                "AI Assistant",
                image,
                "AI Conversation Assistant",
                menu
            )
            
            # Run tray in separate thread
            tray_thread = threading.Thread(target=self.system_tray.run, daemon=True)
            tray_thread.start()
            
        except Exception as e:
            logger.error(f"Failed to create system tray: {e}")
    
    async def _setup_socket_handlers(self):
        """Set up Socket.IO event handlers"""
        
        @self.socket_client.event
        async def connect():
            logger.info("Connected to server via Socket.IO")
        
        @self.socket_client.event
        async def disconnect():
            logger.warning("Disconnected from server")
        
        @self.socket_client.event
        async def ai_suggestion(data):
            """Handle AI suggestions from server"""
            try:
                suggestions = data.get('suggestions', [])
                conversation_id = data.get('conversation_id')
                
                if conversation_id == self.current_conversation_id:
                    await self._display_suggestions(suggestions)
                    
            except Exception as e:
                logger.error(f"Error handling AI suggestion: {e}")
        
        @self.socket_client.event
        async def objection_detected(data):
            """Handle objection detection"""
            try:
                objection = data.get('objection', {})
                responses = data.get('suggested_responses', [])
                
                # Highlight objection and show responses
                await self._highlight_objection(objection, responses)
                
            except Exception as e:
                logger.error(f"Error handling objection detection: {e}")
        
        @self.socket_client.event
        async def conversation_analysis(data):
            """Handle conversation analysis updates"""
            try:
                analysis = data.get('analysis', {})
                
                # Update overlay with analysis
                if self.overlay_window:
                    self.overlay_window.update_analysis(analysis)
                    
            except Exception as e:
                logger.error(f"Error handling conversation analysis: {e}")
    
    async def _on_speech_detected(self, text: str, speaker: str, timestamp: datetime):
        """Handle speech detection from audio manager"""
        try:
            if not self.current_conversation_id:
                # Start new conversation
                self.current_conversation_id = await self.api_client.start_conversation({
                    "type": "meeting",
                    "platform": "desktop",
                    "started_at": timestamp.isoformat()
                })
            
            # Send speech data to server for analysis
            await self.socket_client.emit('speech_detected', {
                "conversation_id": self.current_conversation_id,
                "text": text,
                "speaker": speaker,
                "timestamp": timestamp.isoformat()
            })
            
            # Update overlay with latest speech
            if self.overlay_window:
                self.overlay_window.add_speech(text, speaker, timestamp)
            
            # Store conversation data
            self.conversation_data.append({
                "text": text,
                "speaker": speaker,
                "timestamp": timestamp.isoformat()
            })
            
            logger.info(f"Speech detected ({speaker}): {text}")
            
        except Exception as e:
            logger.error(f"Error handling speech detection: {e}")
    
    async def _display_suggestions(self, suggestions: List[Dict[str, Any]]):
        """Display AI suggestions in overlay"""
        try:
            if self.overlay_window:
                self.overlay_window.show_suggestions(suggestions)
            
        except Exception as e:
            logger.error(f"Error displaying suggestions: {e}")
    
    async def _highlight_objection(self, objection: Dict[str, Any], responses: List[str]):
        """Highlight detected objection and show responses"""
        try:
            if self.overlay_window:
                self.overlay_window.highlight_objection(objection, responses)
            
        except Exception as e:
            logger.error(f"Error highlighting objection: {e}")
    
    def _toggle_recording(self, icon=None, item=None):
        """Toggle audio recording"""
        try:
            if not self.is_recording:
                # Start recording
                asyncio.create_task(self._start_recording())
            else:
                # Stop recording
                asyncio.create_task(self._stop_recording())
                
        except Exception as e:
            logger.error(f"Error toggling recording: {e}")
    
    async def _start_recording(self):
        """Start audio recording"""
        try:
            if self.audio_manager:
                await self.audio_manager.start_recording()
                self.is_recording = True
                
                # Update UI
                if self.overlay_window:
                    self.overlay_window.set_recording_status(True)
                
                logger.info("Recording started")
                
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            messagebox.showerror("Recording Error", f"Failed to start recording: {e}")
    
    async def _stop_recording(self):
        """Stop audio recording"""
        try:
            if self.audio_manager:
                await self.audio_manager.stop_recording()
                self.is_recording = False
                
                # Update UI
                if self.overlay_window:
                    self.overlay_window.set_recording_status(False)
                
                # End conversation
                if self.current_conversation_id:
                    await self.api_client.end_conversation(
                        self.current_conversation_id,
                        {"ended_at": datetime.utcnow().isoformat()}
                    )
                    self.current_conversation_id = None
                
                logger.info("Recording stopped")
                
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
    
    def _on_suggestion_click(self, suggestion: Dict[str, Any]):
        """Handle suggestion click"""
        try:
            # Copy suggestion to clipboard
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(suggestion.get('text', ''))
            root.destroy()
            
            logger.info(f"Suggestion copied to clipboard: {suggestion.get('text', '')}")
            
        except Exception as e:
            logger.error(f"Error handling suggestion click: {e}")
    
    def _show_overlay(self, icon=None, item=None):
        """Show overlay window"""
        if self.overlay_window:
            self.overlay_window.show()
    
    def _open_settings(self, icon=None, item=None):
        """Open settings window"""
        if self.settings_window:
            self.settings_window.show()
    
    def _open_dashboard(self, icon=None, item=None):
        """Open dashboard window"""
        if self.dashboard_window:
            self.dashboard_window.show()
    
    def _on_settings_changed(self, new_settings: Dict[str, Any]):
        """Handle settings changes"""
        try:
            # Update settings
            for key, value in new_settings.items():
                setattr(self.settings, key, value)
            
            # Save settings
            self.settings.save()
            
            # Apply changes
            if 'THEME' in new_settings:
                ctk.set_appearance_mode(new_settings['THEME'])
            
            logger.info("Settings updated")
            
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
    
    async def _test_audio_devices(self):
        """Test audio devices"""
        try:
            if self.audio_manager:
                devices = await self.audio_manager.get_available_devices()
                return devices
            return []
            
        except Exception as e:
            logger.error(f"Error testing audio devices: {e}")
            return []
    
    def _on_conversation_selected(self, conversation_id: str):
        """Handle conversation selection from dashboard"""
        try:
            # Load conversation data
            asyncio.create_task(self._load_conversation(conversation_id))
            
        except Exception as e:
            logger.error(f"Error selecting conversation: {e}")
    
    async def _load_conversation(self, conversation_id: str):
        """Load conversation data"""
        try:
            conversation = await self.api_client.get_conversation(conversation_id)
            
            if self.overlay_window:
                self.overlay_window.load_conversation(conversation)
                
        except Exception as e:
            logger.error(f"Error loading conversation: {e}")
    
    def _quit_application(self, icon=None, item=None):
        """Quit application"""
        try:
            logger.info("Shutting down application...")
            
            # Stop recording if active
            if self.is_recording:
                asyncio.create_task(self._stop_recording())
            
            # Cleanup resources
            asyncio.create_task(self._cleanup())
            
            # Stop system tray
            if self.system_tray:
                self.system_tray.stop()
            
            # Exit
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            sys.exit(1)
    
    async def _cleanup(self):
        """Cleanup resources"""
        try:
            self.is_running = False
            
            # Cleanup audio manager
            if self.audio_manager:
                await self.audio_manager.cleanup()
            
            # Disconnect socket
            if self.socket_client:
                await self.socket_client.disconnect()
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def run(self):
        """Run the application"""
        try:
            # Create event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize application
            if not loop.run_until_complete(self.initialize()):
                return
            
            # Keep the application running
            try:
                while self.is_running:
                    loop.run_until_complete(asyncio.sleep(0.1))
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
            
            # Cleanup
            loop.run_until_complete(self._cleanup())
            
        except Exception as e:
            logger.error(f"Error running application: {e}")
            messagebox.showerror("Application Error", f"Application error: {e}")


def main():
    """Main entry point"""
    try:
        # Create and run application
        app = AIConversationAssistant()
        app.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        messagebox.showerror("Fatal Error", f"Fatal application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
