"""
Keyboard Shortcuts Manager - Cluely.ai-style hotkeys and shortcuts
Provides global hotkeys for quick access to AI assistant functions
"""

import asyncio
from typing import Dict, Callable, Any, Optional
import keyboard
import threading
from loguru import logger

from desktop.config.settings import DesktopSettings


class KeyboardShortcutManager:
    """Manages global keyboard shortcuts - exact Cluely.ai functionality"""
    
    def __init__(self, settings: DesktopSettings):
        self.settings = settings
        self.shortcuts = {}
        self.callbacks = {}
        self.is_active = False
        
        # Default shortcuts (Cluely.ai style)
        self.default_shortcuts = {
            "toggle_recording": settings.HOTKEY_TOGGLE_RECORDING,
            "show_hide_overlay": settings.HOTKEY_SHOW_HIDE,
            "quick_note": settings.HOTKEY_QUICK_NOTE,
            "copy_last_suggestion": settings.HOTKEY_COPY_LAST_SUGGESTION,
            "emergency_stop": "ctrl+shift+esc",
            "focus_teleprompter": "ctrl+shift+t",
            "next_suggestion": "ctrl+shift+down",
            "previous_suggestion": "ctrl+shift+up",
            "accept_suggestion": "ctrl+shift+enter",
            "reject_suggestion": "ctrl+shift+delete",
            "open_settings": "ctrl+shift+s",
            "open_dashboard": "ctrl+shift+d",
            "mute_notifications": "ctrl+shift+m",
            "screenshot_overlay": "ctrl+shift+p",
            "export_conversation": "ctrl+shift+e"
        }
    
    def initialize(self):
        """Initialize keyboard shortcuts"""
        try:
            logger.info("Initializing keyboard shortcuts...")
            
            # Set up default shortcuts
            for action, hotkey in self.default_shortcuts.items():
                self.register_shortcut(action, hotkey)
            
            self.is_active = True
            logger.success("Keyboard shortcuts initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize keyboard shortcuts: {e}")
            raise
    
    def register_shortcut(self, action: str, hotkey: str, callback: Optional[Callable] = None):
        """Register a keyboard shortcut"""
        try:
            if action in self.shortcuts:
                # Unregister existing shortcut
                keyboard.remove_hotkey(self.shortcuts[action])
            
            # Register new shortcut
            hook_id = keyboard.add_hotkey(
                hotkey,
                lambda a=action: self._handle_shortcut(a),
                suppress=False  # Don't suppress the key
            )
            
            self.shortcuts[action] = hook_id
            
            if callback:
                self.callbacks[action] = callback
            
            logger.debug(f"Registered shortcut: {hotkey} -> {action}")
            
        except Exception as e:
            logger.error(f"Error registering shortcut {action}: {e}")
    
    def set_callback(self, action: str, callback: Callable):
        """Set callback for a specific action"""
        self.callbacks[action] = callback
    
    def _handle_shortcut(self, action: str):
        """Handle shortcut activation"""
        try:
            logger.info(f"Shortcut activated: {action}")
            
            # Call registered callback if available
            if action in self.callbacks:
                callback = self.callbacks[action]
                if asyncio.iscoroutinefunction(callback):
                    # Run async callback in thread
                    def run_async():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(callback())
                        loop.close()
                    
                    thread = threading.Thread(target=run_async)
                    thread.daemon = True
                    thread.start()
                else:
                    callback()
            else:
                # Handle built-in shortcuts
                self._handle_builtin_shortcut(action)
            
        except Exception as e:
            logger.error(f"Error handling shortcut {action}: {e}")
    
    def _handle_builtin_shortcut(self, action: str):
        """Handle built-in shortcut actions"""
        try:
            if action == "emergency_stop":
                logger.warning("Emergency stop activated")
                # TODO: Emergency stop functionality
            
            elif action == "mute_notifications":
                logger.info("Notifications muted via shortcut")
                # TODO: Toggle notification mute
            
            elif action == "screenshot_overlay":
                logger.info("Screenshot overlay requested")
                # TODO: Screenshot functionality
            
            else:
                logger.warning(f"No handler for built-in shortcut: {action}")
            
        except Exception as e:
            logger.error(f"Error handling built-in shortcut {action}: {e}")
    
    def update_shortcut(self, action: str, new_hotkey: str):
        """Update an existing shortcut"""
        try:
            if action in self.shortcuts:
                # Remove old shortcut
                keyboard.remove_hotkey(self.shortcuts[action])
            
            # Register new shortcut
            self.register_shortcut(action, new_hotkey, self.callbacks.get(action))
            
            logger.info(f"Updated shortcut {action}: {new_hotkey}")
            
        except Exception as e:
            logger.error(f"Error updating shortcut {action}: {e}")
    
    def remove_shortcut(self, action: str):
        """Remove a keyboard shortcut"""
        try:
            if action in self.shortcuts:
                keyboard.remove_hotkey(self.shortcuts[action])
                del self.shortcuts[action]
                
                if action in self.callbacks:
                    del self.callbacks[action]
                
                logger.info(f"Removed shortcut: {action}")
            
        except Exception as e:
            logger.error(f"Error removing shortcut {action}: {e}")
    
    def get_shortcuts(self) -> Dict[str, str]:
        """Get current shortcuts mapping"""
        return {
            action: self._get_hotkey_for_action(action)
            for action in self.shortcuts.keys()
        }
    
    def _get_hotkey_for_action(self, action: str) -> str:
        """Get hotkey string for action (reverse lookup)"""
        # This is a simplified implementation
        # In practice, you'd need to store the hotkey strings
        return self.default_shortcuts.get(action, "unknown")
    
    def disable_shortcuts(self):
        """Temporarily disable all shortcuts"""
        try:
            for hook_id in self.shortcuts.values():
                keyboard.remove_hotkey(hook_id)
            
            self.is_active = False
            logger.info("Keyboard shortcuts disabled")
            
        except Exception as e:
            logger.error(f"Error disabling shortcuts: {e}")
    
    def enable_shortcuts(self):
        """Re-enable shortcuts after disabling"""
        try:
            if not self.is_active:
                # Re-register all shortcuts
                for action, hotkey in self.default_shortcuts.items():
                    self.register_shortcut(action, hotkey, self.callbacks.get(action))
                
                self.is_active = True
                logger.info("Keyboard shortcuts enabled")
            
        except Exception as e:
            logger.error(f"Error enabling shortcuts: {e}")
    
    def cleanup(self):
        """Clean up keyboard shortcuts"""
        try:
            for hook_id in self.shortcuts.values():
                keyboard.remove_hotkey(hook_id)
            
            self.shortcuts.clear()
            self.callbacks.clear()
            self.is_active = False
            
            logger.info("Keyboard shortcuts cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up shortcuts: {e}")


class ShortcutActions:
    """Predefined shortcut actions for Cluely.ai functionality"""
    
    @staticmethod
    async def toggle_recording():
        """Toggle recording state"""
        logger.info("Toggle recording shortcut activated")
        # This will be connected to the main app's toggle function
    
    @staticmethod
    async def show_hide_overlay():
        """Show/hide overlay window"""
        logger.info("Show/hide overlay shortcut activated")
        # This will be connected to the overlay window's toggle function
    
    @staticmethod
    async def quick_note():
        """Open quick note dialog"""
        logger.info("Quick note shortcut activated")
        # This will open a quick note input dialog
    
    @staticmethod
    async def copy_last_suggestion():
        """Copy the last AI suggestion to clipboard"""
        logger.info("Copy last suggestion shortcut activated")
        # This will copy the most recent suggestion to clipboard
    
    @staticmethod
    async def focus_teleprompter():
        """Focus on teleprompter tab"""
        logger.info("Focus teleprompter shortcut activated")
        # This will switch to and focus the teleprompter tab
    
    @staticmethod
    async def next_suggestion():
        """Navigate to next suggestion"""
        logger.info("Next suggestion shortcut activated")
        # This will highlight the next suggestion in the list
    
    @staticmethod
    async def previous_suggestion():
        """Navigate to previous suggestion"""
        logger.info("Previous suggestion shortcut activated")
        # This will highlight the previous suggestion in the list
    
    @staticmethod
    async def accept_suggestion():
        """Accept/use current suggestion"""
        logger.info("Accept suggestion shortcut activated")
        # This will copy and mark the current suggestion as used
    
    @staticmethod
    async def reject_suggestion():
        """Reject/dismiss current suggestion"""
        logger.info("Reject suggestion shortcut activated")
        # This will dismiss the current suggestion
    
    @staticmethod
    async def open_settings():
        """Open settings window"""
        logger.info("Open settings shortcut activated")
        # This will open the settings window
    
    @staticmethod
    async def open_dashboard():
        """Open analytics dashboard"""
        logger.info("Open dashboard shortcut activated")
        # This will open the analytics dashboard
    
    @staticmethod
    async def mute_notifications():
        """Toggle notification mute"""
        logger.info("Mute notifications shortcut activated")
        # This will toggle notification mute state
    
    @staticmethod
    async def screenshot_overlay():
        """Take screenshot of overlay"""
        logger.info("Screenshot overlay shortcut activated")
        # This will capture a screenshot of the overlay
    
    @staticmethod
    async def export_conversation():
        """Export current conversation"""
        logger.info("Export conversation shortcut activated")
        # This will export the current conversation data
