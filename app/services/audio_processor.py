"""
Real-time audio processing for conversation capture and analysis
"""

import asyncio
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any, List
import numpy as np
import pyaudio
import webrtcvad
import wave
import io
from datetime import datetime
import speech_recognition as sr
import whisper
from loguru import logger

from app.core.config import settings


class AudioProcessor:
    """Real-time audio capture and processing"""
    
    def __init__(self):
        self.is_ready = False
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.vad = None
        self.recognizer = None
        self.whisper_model = None
        self.pyaudio_instance = None
        self.stream = None
        self.processing_thread = None
        self.callback_functions = []
        
        # Audio settings
        self.sample_rate = settings.AUDIO_SAMPLE_RATE
        self.chunk_size = settings.AUDIO_CHUNK_SIZE
        self.channels = settings.AUDIO_CHANNELS
        self.format = pyaudio.paInt16
        
        # VAD settings
        self.vad_mode = 3  # Most aggressive VAD
        self.frame_duration = 30  # 30ms frames
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        
        # Speech detection
        self.silence_threshold = 0.5  # seconds
        self.min_speech_duration = 1.0  # seconds
        self.max_speech_duration = 30.0  # seconds
        
        # Buffer for continuous speech
        self.speech_buffer = []
        self.silence_counter = 0
        self.is_speaking = False
        
    async def initialize(self):
        """Initialize audio processing components"""
        try:
            logger.info("Initializing Audio Processor...")
            
            # Initialize PyAudio
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # Initialize VAD
            self.vad = webrtcvad.Vad(self.vad_mode)
            
            # Initialize speech recognizer
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            
            # Initialize Whisper model
            if settings.WHISPER_API_KEY:
                logger.info("Using OpenAI Whisper API")
            else:
                logger.info("Loading local Whisper model...")
                self.whisper_model = whisper.load_model("base")
            
            self.is_ready = True
            logger.success("Audio Processor initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize Audio Processor: {e}")
            raise
    
    def add_callback(self, callback: Callable[[str, str, datetime], None]):
        """Add callback function for processed speech"""
        self.callback_functions.append(callback)
    
    def start_recording(self, device_index: Optional[int] = None):
        """Start real-time audio recording"""
        try:
            if self.is_recording:
                logger.warning("Already recording")
                return
            
            logger.info("Starting audio recording...")
            
            # Open audio stream
            self.stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_recording = True
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._process_audio_loop)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            logger.success("Audio recording started")
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            raise
    
    def stop_recording(self):
        """Stop audio recording"""
        try:
            if not self.is_recording:
                return
            
            logger.info("Stopping audio recording...")
            
            self.is_recording = False
            
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            # Wait for processing thread to finish
            if self.processing_thread:
                self.processing_thread.join(timeout=2.0)
            
            logger.success("Audio recording stopped")
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for real-time audio data"""
        if self.is_recording:
            self.audio_queue.put((in_data, time.time()))
        return (None, pyaudio.paContinue)
    
    def _process_audio_loop(self):
        """Main audio processing loop"""
        logger.info("Audio processing loop started")
        
        while self.is_recording:
            try:
                # Get audio data with timeout
                try:
                    audio_data, timestamp = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Convert to numpy array
                audio_np = np.frombuffer(audio_data, dtype=np.int16)
                
                # Process audio chunk
                self._process_audio_chunk(audio_np, timestamp)
                
            except Exception as e:
                logger.error(f"Error in audio processing loop: {e}")
        
        logger.info("Audio processing loop ended")
    
    def _process_audio_chunk(self, audio_data: np.ndarray, timestamp: float):
        """Process a single chunk of audio data"""
        try:
            # Ensure correct frame size for VAD
            if len(audio_data) != self.frame_size:
                # Pad or truncate to correct size
                if len(audio_data) < self.frame_size:
                    audio_data = np.pad(audio_data, (0, self.frame_size - len(audio_data)))
                else:
                    audio_data = audio_data[:self.frame_size]
            
            # Convert to bytes for VAD
            audio_bytes = audio_data.tobytes()
            
            # Voice Activity Detection
            is_speech = self.vad.is_speech(audio_bytes, self.sample_rate)
            
            if is_speech:
                # Add to speech buffer
                self.speech_buffer.append(audio_data)
                self.silence_counter = 0
                
                if not self.is_speaking:
                    self.is_speaking = True
                    logger.debug("Speech started")
            else:
                # Increment silence counter
                self.silence_counter += 1
                
                # If we were speaking and now have enough silence, process the speech
                if self.is_speaking and self.silence_counter > (self.silence_threshold * 1000 / self.frame_duration):
                    self._process_speech_segment(timestamp)
                    self.is_speaking = False
                    self.speech_buffer = []
                    self.silence_counter = 0
            
            # Prevent buffer from getting too large
            if len(self.speech_buffer) > (self.max_speech_duration * 1000 / self.frame_duration):
                self._process_speech_segment(timestamp)
                self.speech_buffer = []
                self.is_speaking = False
                
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
    
    def _process_speech_segment(self, timestamp: float):
        """Process a complete speech segment"""
        try:
            if not self.speech_buffer:
                return
            
            # Check minimum duration
            duration = len(self.speech_buffer) * self.frame_duration / 1000
            if duration < self.min_speech_duration:
                return
            
            logger.debug(f"Processing speech segment of {duration:.2f} seconds")
            
            # Combine audio chunks
            combined_audio = np.concatenate(self.speech_buffer)
            
            # Convert to speech recognition format
            audio_data = sr.AudioData(
                combined_audio.tobytes(),
                self.sample_rate,
                2  # 2 bytes per sample for int16
            )
            
            # Transcribe speech
            asyncio.create_task(self._transcribe_audio(audio_data, timestamp))
            
        except Exception as e:
            logger.error(f"Error processing speech segment: {e}")
    
    async def _transcribe_audio(self, audio_data: sr.AudioData, timestamp: float):
        """Transcribe audio to text"""
        try:
            text = None
            speaker = "unknown"
            
            # Try different transcription methods
            if settings.WHISPER_API_KEY:
                # Use OpenAI Whisper API
                text = await self._transcribe_with_whisper_api(audio_data)
            elif self.whisper_model:
                # Use local Whisper model
                text = await self._transcribe_with_local_whisper(audio_data)
            else:
                # Use Google Speech Recognition as fallback
                text = await self._transcribe_with_google(audio_data)
            
            if text and text.strip():
                # Determine speaker (simplified - in real implementation, use speaker diarization)
                speaker = self._identify_speaker(audio_data)
                
                # Create timestamp
                dt = datetime.fromtimestamp(timestamp)
                
                # Call all registered callbacks
                for callback in self.callback_functions:
                    try:
                        await callback(text.strip(), speaker, dt)
                    except Exception as e:
                        logger.error(f"Error in callback: {e}")
                
                logger.info(f"Transcribed ({speaker}): {text.strip()}")
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
    
    async def _transcribe_with_whisper_api(self, audio_data: sr.AudioData) -> Optional[str]:
        """Transcribe using OpenAI Whisper API"""
        try:
            # Convert audio data to WAV format
            wav_data = io.BytesIO()
            with wave.open(wav_data, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 2 bytes for int16
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data.frame_data)
            
            wav_data.seek(0)
            
            # TODO: Implement OpenAI Whisper API call
            # This would require the actual OpenAI client setup
            return None
            
        except Exception as e:
            logger.error(f"Error with Whisper API: {e}")
            return None
    
    async def _transcribe_with_local_whisper(self, audio_data: sr.AudioData) -> Optional[str]:
        """Transcribe using local Whisper model"""
        try:
            # Convert audio data to numpy array
            audio_np = np.frombuffer(audio_data.frame_data, dtype=np.int16).astype(np.float32)
            audio_np = audio_np / 32768.0  # Normalize to [-1, 1]
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(audio_np)
            return result["text"]
            
        except Exception as e:
            logger.error(f"Error with local Whisper: {e}")
            return None
    
    async def _transcribe_with_google(self, audio_data: sr.AudioData) -> Optional[str]:
        """Transcribe using Google Speech Recognition"""
        try:
            text = self.recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Google Speech Recognition error: {e}")
            return None
    
    def _identify_speaker(self, audio_data: sr.AudioData) -> str:
        """Identify speaker (simplified implementation)"""
        # In a real implementation, this would use speaker diarization
        # For now, we'll use a simple heuristic or return "user"
        return "user"
    
    def get_available_devices(self) -> List[Dict[str, Any]]:
        """Get list of available audio input devices"""
        devices = []
        
        if not self.pyaudio_instance:
            return devices
        
        try:
            for i in range(self.pyaudio_instance.get_device_count()):
                device_info = self.pyaudio_instance.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': device_info['defaultSampleRate']
                    })
        except Exception as e:
            logger.error(f"Error getting audio devices: {e}")
        
        return devices
    
    async def cleanup(self):
        """Cleanup audio resources"""
        try:
            self.stop_recording()
            
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
            
            self.is_ready = False
            logger.info("Audio Processor cleaned up")
            
        except Exception as e:
            logger.error(f"Error during audio cleanup: {e}")
