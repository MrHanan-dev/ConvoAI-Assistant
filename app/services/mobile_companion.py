"""
Mobile Companion API - Cluely.ai mobile features
Provides mobile app integration and companion functionality
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.core.config import settings


class MobileCompanionManager:
    """Manages mobile companion app connections and features"""
    
    def __init__(self):
        self.active_connections = {}  # device_id -> WebSocket
        self.mobile_sessions = {}     # session_id -> session_data
        self.sync_queue = {}          # device_id -> pending_sync_data
        
        # Mobile features that match Cluely.ai
        self.mobile_features = {
            "conversation_sync": True,
            "remote_control": True,
            "quick_notes": True,
            "suggestion_review": True,
            "analytics_view": True,
            "notification_relay": True,
            "offline_mode": True,
            "voice_commands": True
        }
    
    async def connect_mobile_device(self, websocket: WebSocket, device_id: str):
        """Connect mobile device for companion features"""
        try:
            await websocket.accept()
            self.active_connections[device_id] = websocket
            
            # Send initial sync data
            await self._send_initial_sync(websocket, device_id)
            
            logger.info(f"Mobile device connected: {device_id}")
            
            # Handle mobile messages
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_mobile_message(device_id, message)
                    
            except WebSocketDisconnect:
                await self._disconnect_mobile_device(device_id)
                
        except Exception as e:
            logger.error(f"Error in mobile connection: {e}")
            await self._disconnect_mobile_device(device_id)
    
    async def _send_initial_sync(self, websocket: WebSocket, device_id: str):
        """Send initial sync data to mobile device"""
        try:
            sync_data = {
                "type": "initial_sync",
                "timestamp": datetime.utcnow().isoformat(),
                "features": self.mobile_features,
                "active_conversations": await self._get_active_conversations(),
                "recent_suggestions": await self._get_recent_suggestions(),
                "user_settings": await self._get_mobile_settings()
            }
            
            await websocket.send_text(json.dumps(sync_data))
            
        except Exception as e:
            logger.error(f"Error sending initial sync: {e}")
    
    async def _handle_mobile_message(self, device_id: str, message: Dict[str, Any]):
        """Handle message from mobile device"""
        try:
            message_type = message.get("type")
            
            if message_type == "remote_control":
                await self._handle_remote_control(device_id, message)
            
            elif message_type == "quick_note":
                await self._handle_quick_note(device_id, message)
            
            elif message_type == "suggestion_feedback":
                await self._handle_suggestion_feedback(device_id, message)
            
            elif message_type == "voice_command":
                await self._handle_voice_command(device_id, message)
            
            elif message_type == "settings_update":
                await self._handle_settings_update(device_id, message)
            
            else:
                logger.warning(f"Unknown mobile message type: {message_type}")
            
        except Exception as e:
            logger.error(f"Error handling mobile message: {e}")
    
    async def _handle_remote_control(self, device_id: str, message: Dict[str, Any]):
        """Handle remote control commands from mobile"""
        try:
            command = message.get("command")
            
            if command == "start_recording":
                # Signal desktop app to start recording
                await self._send_desktop_command("start_recording")
                await self._notify_mobile_device(device_id, "Recording started")
            
            elif command == "stop_recording":
                # Signal desktop app to stop recording
                await self._send_desktop_command("stop_recording")
                await self._notify_mobile_device(device_id, "Recording stopped")
            
            elif command == "show_overlay":
                await self._send_desktop_command("show_overlay")
                await self._notify_mobile_device(device_id, "Overlay shown")
            
            elif command == "hide_overlay":
                await self._send_desktop_command("hide_overlay")
                await self._notify_mobile_device(device_id, "Overlay hidden")
            
            elif command == "emergency_stop":
                await self._send_desktop_command("emergency_stop")
                await self._notify_mobile_device(device_id, "Emergency stop activated")
            
        except Exception as e:
            logger.error(f"Error handling remote control: {e}")
    
    async def _handle_quick_note(self, device_id: str, message: Dict[str, Any]):
        """Handle quick note from mobile device"""
        try:
            note_text = message.get("note", "")
            timestamp = message.get("timestamp", datetime.utcnow().isoformat())
            
            # Store note and sync with desktop
            note_data = {
                "type": "quick_note",
                "text": note_text,
                "timestamp": timestamp,
                "source": "mobile",
                "device_id": device_id
            }
            
            # Send to desktop app
            await self._send_desktop_command("add_note", note_data)
            
            # Confirm to mobile
            await self._notify_mobile_device(device_id, "Note added")
            
        except Exception as e:
            logger.error(f"Error handling quick note: {e}")
    
    async def _handle_suggestion_feedback(self, device_id: str, message: Dict[str, Any]):
        """Handle suggestion feedback from mobile"""
        try:
            suggestion_id = message.get("suggestion_id")
            feedback = message.get("feedback")  # "positive", "negative", "used"
            
            # Process feedback
            feedback_data = {
                "suggestion_id": suggestion_id,
                "feedback": feedback,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "mobile"
            }
            
            # Send to analytics system
            await self._process_suggestion_feedback(feedback_data)
            
            # Confirm to mobile
            await self._notify_mobile_device(device_id, "Feedback recorded")
            
        except Exception as e:
            logger.error(f"Error handling suggestion feedback: {e}")
    
    async def _handle_voice_command(self, device_id: str, message: Dict[str, Any]):
        """Handle voice command from mobile"""
        try:
            command = message.get("command", "").lower()
            
            # Process voice commands
            if "start recording" in command:
                await self._send_desktop_command("start_recording")
            
            elif "stop recording" in command:
                await self._send_desktop_command("stop_recording")
            
            elif "show suggestions" in command:
                await self._send_desktop_command("show_suggestions")
            
            elif "hide overlay" in command:
                await self._send_desktop_command("hide_overlay")
            
            elif "take note" in command:
                # Extract note text from command
                note_text = command.replace("take note", "").strip()
                if note_text:
                    await self._handle_quick_note(device_id, {"note": note_text})
            
            else:
                await self._notify_mobile_device(device_id, "Voice command not recognized")
            
        except Exception as e:
            logger.error(f"Error handling voice command: {e}")
    
    async def _handle_settings_update(self, device_id: str, message: Dict[str, Any]):
        """Handle settings update from mobile"""
        try:
            settings_data = message.get("settings", {})
            
            # Update mobile-specific settings
            await self._update_mobile_settings(device_id, settings_data)
            
            # Sync with desktop if needed
            if settings_data.get("sync_with_desktop", False):
                await self._send_desktop_command("update_settings", settings_data)
            
            await self._notify_mobile_device(device_id, "Settings updated")
            
        except Exception as e:
            logger.error(f"Error handling settings update: {e}")
    
    async def sync_conversation_to_mobile(self, conversation_data: Dict[str, Any]):
        """Sync conversation data to all connected mobile devices"""
        try:
            sync_message = {
                "type": "conversation_sync",
                "timestamp": datetime.utcnow().isoformat(),
                "conversation": conversation_data
            }
            
            # Send to all connected devices
            for device_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_text(json.dumps(sync_message))
                except Exception as e:
                    logger.error(f"Error syncing to device {device_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error syncing conversation to mobile: {e}")
    
    async def send_suggestion_to_mobile(self, suggestions: List[Dict[str, Any]]):
        """Send AI suggestions to mobile devices for review"""
        try:
            suggestion_message = {
                "type": "suggestions_update",
                "timestamp": datetime.utcnow().isoformat(),
                "suggestions": suggestions
            }
            
            # Send to all connected devices
            for device_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_text(json.dumps(suggestion_message))
                except Exception as e:
                    logger.error(f"Error sending suggestions to device {device_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error sending suggestions to mobile: {e}")
    
    async def send_analytics_to_mobile(self, analytics_data: Dict[str, Any]):
        """Send analytics data to mobile devices"""
        try:
            analytics_message = {
                "type": "analytics_update",
                "timestamp": datetime.utcnow().isoformat(),
                "analytics": analytics_data
            }
            
            # Send to all connected devices
            for device_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_text(json.dumps(analytics_message))
                except Exception as e:
                    logger.error(f"Error sending analytics to device {device_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error sending analytics to mobile: {e}")
    
    async def _send_desktop_command(self, command: str, data: Optional[Dict[str, Any]] = None):
        """Send command to desktop application"""
        try:
            # This would integrate with the desktop app's command system
            # For now, we'll log the command
            logger.info(f"Desktop command: {command}, data: {data}")
            
        except Exception as e:
            logger.error(f"Error sending desktop command: {e}")
    
    async def _notify_mobile_device(self, device_id: str, message: str):
        """Send notification to specific mobile device"""
        try:
            if device_id in self.active_connections:
                notification = {
                    "type": "notification",
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self.active_connections[device_id].send_text(json.dumps(notification))
            
        except Exception as e:
            logger.error(f"Error notifying mobile device: {e}")
    
    async def _disconnect_mobile_device(self, device_id: str):
        """Handle mobile device disconnection"""
        try:
            if device_id in self.active_connections:
                del self.active_connections[device_id]
            
            if device_id in self.sync_queue:
                del self.sync_queue[device_id]
            
            logger.info(f"Mobile device disconnected: {device_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting mobile device: {e}")
    
    async def _get_active_conversations(self) -> List[Dict[str, Any]]:
        """Get active conversations for mobile sync"""
        # This would query the database for active conversations
        return []
    
    async def _get_recent_suggestions(self) -> List[Dict[str, Any]]:
        """Get recent suggestions for mobile sync"""
        # This would query recent AI suggestions
        return []
    
    async def _get_mobile_settings(self) -> Dict[str, Any]:
        """Get mobile-specific settings"""
        return {
            "notifications_enabled": True,
            "voice_commands_enabled": True,
            "auto_sync": True,
            "offline_mode": False
        }
    
    async def _update_mobile_settings(self, device_id: str, settings: Dict[str, Any]):
        """Update settings for specific mobile device"""
        # This would update mobile-specific settings in database
        logger.info(f"Updated settings for device {device_id}: {settings}")
    
    async def _process_suggestion_feedback(self, feedback_data: Dict[str, Any]):
        """Process suggestion feedback for ML improvement"""
        # This would send feedback to the AI learning system
        logger.info(f"Processing suggestion feedback: {feedback_data}")
    
    def get_connected_devices(self) -> List[str]:
        """Get list of connected mobile devices"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """Get number of connected mobile devices"""
        return len(self.active_connections)
