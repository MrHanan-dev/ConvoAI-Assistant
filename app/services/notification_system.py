"""
Notification System for Cluely.ai-style alerts and popups
Handles objection alerts, suggestion notifications, and system messages
"""

import asyncio
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import winsound  # Windows sound system
from loguru import logger
import json

from desktop.config.settings import DesktopSettings


class NotificationManager:
    """Manages all notification types - exact Cluely.ai functionality"""
    
    def __init__(self, settings: DesktopSettings):
        self.settings = settings
        self.active_notifications = []
        self.notification_queue = []
        self.sound_enabled = settings.NOTIFICATION_SOUND
        self.objection_alerts_enabled = settings.OBJECTION_ALERTS
        self.suggestion_popup_enabled = settings.SUGGESTION_POPUP
        
        # Notification types and their configurations
        self.notification_types = {
            "objection_detected": {
                "title": "🚨 Objection Detected",
                "icon": "warning",
                "sound": "SystemExclamation",
                "priority": "high",
                "auto_dismiss": 10000,  # 10 seconds
                "show_popup": True
            },
            "suggestion_ready": {
                "title": "💡 AI Suggestion",
                "icon": "info", 
                "sound": "SystemAsterisk",
                "priority": "medium",
                "auto_dismiss": 5000,  # 5 seconds
                "show_popup": False  # Show in overlay instead
            },
            "win_rate_update": {
                "title": "📊 Win Rate Update",
                "icon": "info",
                "sound": None,
                "priority": "low",
                "auto_dismiss": 3000,  # 3 seconds
                "show_popup": False
            },
            "recording_started": {
                "title": "🎙️ Recording Started",
                "icon": "info",
                "sound": "SystemHand",
                "priority": "medium",
                "auto_dismiss": 2000,  # 2 seconds
                "show_popup": False
            },
            "recording_stopped": {
                "title": "⏹️ Recording Stopped",
                "icon": "info",
                "sound": "SystemHand",
                "priority": "medium", 
                "auto_dismiss": 2000,
                "show_popup": False
            },
            "platform_detected": {
                "title": "🔗 Meeting Platform Detected",
                "icon": "info",
                "sound": "SystemDefault",
                "priority": "low",
                "auto_dismiss": 3000,
                "show_popup": False
            },
            "crm_sync_complete": {
                "title": "✅ CRM Sync Complete",
                "icon": "info",
                "sound": None,
                "priority": "low",
                "auto_dismiss": 2000,
                "show_popup": False
            },
            "error": {
                "title": "❌ Error",
                "icon": "error",
                "sound": "SystemHand",
                "priority": "high",
                "auto_dismiss": 8000,
                "show_popup": True
            },
            "success": {
                "title": "✅ Success",
                "icon": "info",
                "sound": "SystemDefault",
                "priority": "medium",
                "auto_dismiss": 3000,
                "show_popup": False
            }
        }
    
    async def show_objection_alert(self, objection_data: Dict[str, Any]):
        """Show urgent objection detection alert - Core Cluely.ai feature"""
        try:
            if not self.objection_alerts_enabled:
                return
            
            objection_type = objection_data.get("type", "unknown")
            confidence = objection_data.get("confidence", 0)
            suggested_responses = objection_data.get("suggested_responses", [])
            
            message = f"""
🚨 OBJECTION DETECTED: {objection_type.upper()}
Confidence: {confidence:.0%}

Suggested Responses:
{chr(10).join(f"• {response}" for response in suggested_responses[:3])}
            """.strip()
            
            await self._show_notification(
                "objection_detected",
                message,
                extra_data=objection_data
            )
            
            # Create urgent popup for high-confidence objections
            if confidence > 0.8:
                await self._show_urgent_popup(
                    "🚨 High-Confidence Objection Detected!",
                    f"Type: {objection_type}\nConfidence: {confidence:.0%}\n\nCheck teleprompter for responses.",
                    "warning"
                )
            
        except Exception as e:
            logger.error(f"Error showing objection alert: {e}")
    
    async def show_suggestion_notification(self, suggestions: list):
        """Show AI suggestion notification"""
        try:
            if not self.suggestion_popup_enabled or not suggestions:
                return
            
            suggestion_count = len(suggestions)
            top_suggestion = suggestions[0].get("text", "")[:50] + "..."
            
            message = f"""
💡 {suggestion_count} AI Suggestion{'s' if suggestion_count > 1 else ''} Ready
Top: {top_suggestion}
            """.strip()
            
            await self._show_notification(
                "suggestion_ready",
                message,
                extra_data={"suggestions": suggestions}
            )
            
        except Exception as e:
            logger.error(f"Error showing suggestion notification: {e}")
    
    async def show_win_rate_update(self, win_rate: float, trend: str):
        """Show win rate prediction update"""
        try:
            trend_emoji = "📈" if trend == "improving" else "📉" if trend == "declining" else "📊"
            
            message = f"""
{trend_emoji} Win Rate: {win_rate:.0%}
Trend: {trend.title()}
            """.strip()
            
            await self._show_notification(
                "win_rate_update",
                message,
                extra_data={"win_rate": win_rate, "trend": trend}
            )
            
        except Exception as e:
            logger.error(f"Error showing win rate update: {e}")
    
    async def show_recording_status(self, is_recording: bool):
        """Show recording status notification"""
        try:
            notification_type = "recording_started" if is_recording else "recording_stopped"
            message = "Recording started - AI analysis active" if is_recording else "Recording stopped - Analysis complete"
            
            await self._show_notification(
                notification_type,
                message,
                extra_data={"is_recording": is_recording}
            )
            
        except Exception as e:
            logger.error(f"Error showing recording status: {e}")
    
    async def show_platform_detection(self, platform: str, meeting_info: Dict[str, Any]):
        """Show meeting platform detection notification"""
        try:
            meeting_title = meeting_info.get("meeting_title", "Meeting")
            participants = len(meeting_info.get("participants", []))
            
            message = f"""
🔗 {platform.title()} Meeting Detected
Title: {meeting_title}
Participants: {participants}
            """.strip()
            
            await self._show_notification(
                "platform_detected",
                message,
                extra_data={"platform": platform, "meeting_info": meeting_info}
            )
            
        except Exception as e:
            logger.error(f"Error showing platform detection: {e}")
    
    async def show_crm_sync_status(self, crm_name: str, success: bool, details: str = ""):
        """Show CRM synchronization status"""
        try:
            if success:
                message = f"✅ {crm_name} sync complete"
                if details:
                    message += f"\n{details}"
                
                await self._show_notification(
                    "crm_sync_complete",
                    message,
                    extra_data={"crm": crm_name, "success": success}
                )
            else:
                message = f"❌ {crm_name} sync failed"
                if details:
                    message += f"\n{details}"
                
                await self._show_notification(
                    "error",
                    message,
                    extra_data={"crm": crm_name, "success": success}
                )
            
        except Exception as e:
            logger.error(f"Error showing CRM sync status: {e}")
    
    async def show_system_notification(self, title: str, message: str, notification_type: str = "info"):
        """Show general system notification"""
        try:
            type_map = {
                "info": "success",
                "warning": "objection_detected", 
                "error": "error",
                "success": "success"
            }
            
            mapped_type = type_map.get(notification_type, "success")
            
            await self._show_notification(
                mapped_type,
                f"{title}\n{message}",
                extra_data={"custom": True}
            )
            
        except Exception as e:
            logger.error(f"Error showing system notification: {e}")
    
    async def _show_notification(
        self,
        notification_type: str,
        message: str,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        """Internal method to show notification"""
        try:
            if not self.settings.ENABLE_NOTIFICATIONS:
                return
            
            config = self.notification_types.get(notification_type, self.notification_types["success"])
            
            # Play sound if enabled
            if self.sound_enabled and config.get("sound"):
                await self._play_notification_sound(config["sound"])
            
            # Create notification object
            notification = {
                "id": f"{notification_type}_{datetime.utcnow().timestamp()}",
                "type": notification_type,
                "title": config["title"],
                "message": message,
                "timestamp": datetime.utcnow(),
                "priority": config["priority"],
                "auto_dismiss": config["auto_dismiss"],
                "extra_data": extra_data or {}
            }
            
            # Add to active notifications
            self.active_notifications.append(notification)
            
            # Show popup if required
            if config.get("show_popup", False):
                await self._show_urgent_popup(
                    config["title"],
                    message,
                    config["icon"]
                )
            
            # Schedule auto-dismiss
            if config["auto_dismiss"]:
                asyncio.create_task(
                    self._auto_dismiss_notification(notification["id"], config["auto_dismiss"])
                )
            
            logger.info(f"Notification shown: {notification_type}")
            
        except Exception as e:
            logger.error(f"Error in _show_notification: {e}")
    
    async def _play_notification_sound(self, sound_name: str):
        """Play Windows notification sound"""
        try:
            if not self.sound_enabled:
                return
            
            # Map sound names to Windows system sounds
            sound_map = {
                "SystemExclamation": winsound.MB_ICONEXCLAMATION,
                "SystemAsterisk": winsound.MB_ICONASTERISK,
                "SystemHand": winsound.MB_ICONHAND,
                "SystemDefault": winsound.MB_OK
            }
            
            sound_type = sound_map.get(sound_name, winsound.MB_OK)
            
            # Play sound in separate thread to avoid blocking
            def play_sound():
                try:
                    winsound.MessageBeep(sound_type)
                except Exception as e:
                    logger.error(f"Error playing sound: {e}")
            
            thread = threading.Thread(target=play_sound)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error playing notification sound: {e}")
    
    async def _show_urgent_popup(self, title: str, message: str, icon: str = "info"):
        """Show urgent popup window"""
        try:
            # Create popup in main thread
            def show_popup():
                try:
                    root = tk.Tk()
                    root.withdraw()  # Hide main window
                    
                    # Map icon types
                    icon_map = {
                        "info": messagebox.showinfo,
                        "warning": messagebox.showwarning,
                        "error": messagebox.showerror
                    }
                    
                    show_func = icon_map.get(icon, messagebox.showinfo)
                    show_func(title, message)
                    
                    root.destroy()
                    
                except Exception as e:
                    logger.error(f"Error showing popup: {e}")
            
            # Run popup in separate thread
            thread = threading.Thread(target=show_popup)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error in _show_urgent_popup: {e}")
    
    async def _auto_dismiss_notification(self, notification_id: str, delay_ms: int):
        """Auto-dismiss notification after delay"""
        try:
            await asyncio.sleep(delay_ms / 1000)  # Convert ms to seconds
            
            # Remove from active notifications
            self.active_notifications = [
                n for n in self.active_notifications 
                if n["id"] != notification_id
            ]
            
        except Exception as e:
            logger.error(f"Error auto-dismissing notification: {e}")
    
    def get_active_notifications(self) -> list:
        """Get list of active notifications"""
        return self.active_notifications.copy()
    
    def dismiss_notification(self, notification_id: str):
        """Manually dismiss a notification"""
        try:
            self.active_notifications = [
                n for n in self.active_notifications 
                if n["id"] != notification_id
            ]
            
        except Exception as e:
            logger.error(f"Error dismissing notification: {e}")
    
    def clear_all_notifications(self):
        """Clear all active notifications"""
        self.active_notifications.clear()
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update notification settings"""
        try:
            if "ENABLE_NOTIFICATIONS" in new_settings:
                self.settings.ENABLE_NOTIFICATIONS = new_settings["ENABLE_NOTIFICATIONS"]
            
            if "NOTIFICATION_SOUND" in new_settings:
                self.sound_enabled = new_settings["NOTIFICATION_SOUND"]
                self.settings.NOTIFICATION_SOUND = new_settings["NOTIFICATION_SOUND"]
            
            if "OBJECTION_ALERTS" in new_settings:
                self.objection_alerts_enabled = new_settings["OBJECTION_ALERTS"]
                self.settings.OBJECTION_ALERTS = new_settings["OBJECTION_ALERTS"]
            
            if "SUGGESTION_POPUP" in new_settings:
                self.suggestion_popup_enabled = new_settings["SUGGESTION_POPUP"]
                self.settings.SUGGESTION_POPUP = new_settings["SUGGESTION_POPUP"]
            
            logger.info("Notification settings updated")
            
        except Exception as e:
            logger.error(f"Error updating notification settings: {e}")
