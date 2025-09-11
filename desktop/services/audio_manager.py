"""
Audio manager for desktop application
"""

import asyncio
import threading
from typing import Callable, Optional, List, Dict, Any
from datetime import datetime
import pyaudio
import numpy as np
from loguru import logger

from app.services.audio_processor import AudioProcessor


class AudioManager:
    """Desktop audio manager wrapper"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.is_ready = False
        self.transcription_callback = None
    
    async def initialize(self):
        """Initialize audio manager"""
        try:
            await self.audio_processor.initialize()
            self.is_ready = True
            logger.success("Audio Manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Audio Manager: {e}")
            raise
    
    def set_transcription_callback(self, callback: Callable):
        """Set callback for transcription results"""
        self.transcription_callback = callback
        self.audio_processor.add_callback(self._handle_transcription)
    
    async def _handle_transcription(self, text: str, speaker: str, timestamp: datetime):
        """Handle transcription from audio processor"""
        if self.transcription_callback:
            await self.transcription_callback(text, speaker, timestamp)
    
    async def start_recording(self, device_index: Optional[int] = None):
        """Start audio recording"""
        self.audio_processor.start_recording(device_index)
    
    async def stop_recording(self):
        """Stop audio recording"""
        self.audio_processor.stop_recording()
    
    async def get_available_devices(self) -> List[Dict[str, Any]]:
        """Get available audio devices"""
        return self.audio_processor.get_available_devices()
    
    async def cleanup(self):
        """Cleanup audio manager"""
        await self.audio_processor.cleanup()
        self.is_ready = False
