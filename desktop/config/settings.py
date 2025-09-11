"""
Desktop application settings and configuration
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger


class DesktopSettings:
    """Desktop application settings manager"""
    
    def __init__(self):
        # File paths
        self.config_dir = Path.home() / ".ai_assistant"
        self.config_file = self.config_dir / "settings.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Default settings
        self.defaults = {
            # API Configuration
            "API_BASE_URL": "http://localhost:8000",
            "API_KEY": "",
            "SOCKET_URL": "http://localhost:8000",
            
            # UI Settings
            "THEME": "dark",  # dark, light, system
            "COLOR_THEME": "blue",  # blue, green, dark-blue
            "OVERLAY_WIDTH": 450,
            "OVERLAY_HEIGHT": 600,
            "OVERLAY_X": 100,
            "OVERLAY_Y": 100,
            "OVERLAY_OPACITY": 0.95,
            "ALWAYS_ON_TOP": True,
            "AUTO_HIDE": False,
            "MINIMIZE_TO_TRAY": True,
            
            # Audio Settings
            "AUDIO_INPUT_DEVICE": None,  # Auto-select
            "AUDIO_SAMPLE_RATE": 16000,
            "AUDIO_CHUNK_SIZE": 1024,
            "NOISE_REDUCTION": True,
            "VOICE_ACTIVATION_THRESHOLD": 0.3,
            "SILENCE_TIMEOUT": 2.0,
            
            # AI Settings
            "AI_MODEL": "gpt-4",
            "RESPONSE_LANGUAGE": "en",
            "SUGGESTION_CONFIDENCE_THRESHOLD": 0.6,
            "MAX_SUGGESTIONS": 5,
            "AUTO_COPY_SUGGESTIONS": False,
            "ENABLE_OBJECTION_DETECTION": True,
            "ENABLE_SENTIMENT_ANALYSIS": True,
            
            # Privacy Settings
            "RECORD_AUDIO": False,  # For compliance
            "STORE_CONVERSATIONS": True,
            "SHARE_ANALYTICS": False,
            "AUTO_DELETE_AFTER_DAYS": 30,
            
            # Hotkeys
            "HOTKEY_TOGGLE_RECORDING": "ctrl+shift+r",
            "HOTKEY_SHOW_HIDE": "ctrl+shift+h",
            "HOTKEY_QUICK_NOTE": "ctrl+shift+n",
            "HOTKEY_COPY_LAST_SUGGESTION": "ctrl+shift+c",
            
            # Enterprise Features
            "ENABLE_CALL_SHADOW_MODE": False,
            "ENABLE_TEAM_FEATURES": False,
            "CRM_INTEGRATION": "none",  # none, salesforce, hubspot
            
            # Notifications
            "ENABLE_NOTIFICATIONS": True,
            "NOTIFICATION_SOUND": True,
            "OBJECTION_ALERTS": True,
            "SUGGESTION_POPUP": True,
            
            # Performance
            "ENABLE_GPU_ACCELERATION": False,
            "MAX_MEMORY_USAGE_MB": 2048,
            "AUDIO_BUFFER_SIZE": 4096,
            "PROCESSING_THREADS": 2,
            
            # Debug
            "DEBUG_MODE": False,
            "LOG_LEVEL": "INFO",
            "ENABLE_TELEMETRY": True
        }
        
        # Load settings
        self._load_settings()
    
    def _load_settings(self):
        """Load settings from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    saved_settings = json.load(f)
                
                # Merge with defaults
                for key, value in saved_settings.items():
                    if key in self.defaults:
                        setattr(self, key, value)
                
                logger.info("Settings loaded from file")
            else:
                logger.info("Using default settings")
            
            # Set defaults for missing attributes
            for key, value in self.defaults.items():
                if not hasattr(self, key):
                    setattr(self, key, value)
                    
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            # Use defaults
            for key, value in self.defaults.items():
                setattr(self, key, value)
    
    def save(self):
        """Save current settings to file"""
        try:
            settings_dict = {}
            for key in self.defaults.keys():
                if hasattr(self, key):
                    settings_dict[key] = getattr(self, key)
            
            with open(self.config_file, 'w') as f:
                json.dump(settings_dict, f, indent=2)
            
            logger.info("Settings saved to file")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        for key, value in self.defaults.items():
            setattr(self, key, value)
        
        logger.info("Settings reset to defaults")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        return getattr(self, key, default)
    
    def set(self, key: str, value: Any):
        """Set setting value"""
        setattr(self, key, value)
    
    def update(self, settings_dict: Dict[str, Any]):
        """Update multiple settings"""
        for key, value in settings_dict.items():
            if key in self.defaults:
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        result = {}
        for key in self.defaults.keys():
            if hasattr(self, key):
                result[key] = getattr(self, key)
        return result
    
    def validate(self) -> bool:
        """Validate current settings"""
        try:
            # Check required settings
            if not self.API_BASE_URL:
                logger.error("API_BASE_URL is required")
                return False
            
            # Validate ranges
            if not (0.1 <= self.OVERLAY_OPACITY <= 1.0):
                logger.error("OVERLAY_OPACITY must be between 0.1 and 1.0")
                return False
            
            if not (8000 <= self.AUDIO_SAMPLE_RATE <= 48000):
                logger.error("AUDIO_SAMPLE_RATE must be between 8000 and 48000")
                return False
            
            if not (0.0 <= self.VOICE_ACTIVATION_THRESHOLD <= 1.0):
                logger.error("VOICE_ACTIVATION_THRESHOLD must be between 0.0 and 1.0")
                return False
            
            if not (0.0 <= self.SUGGESTION_CONFIDENCE_THRESHOLD <= 1.0):
                logger.error("SUGGESTION_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
                return False
            
            if not (1 <= self.MAX_SUGGESTIONS <= 20):
                logger.error("MAX_SUGGESTIONS must be between 1 and 20")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating settings: {e}")
            return False
