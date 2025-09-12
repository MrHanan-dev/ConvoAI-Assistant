#!/usr/bin/env python3
"""
AI Conversation Assistant - Working Version with Cohere Integration
Real-time conversation analysis with AI-powered responses
"""

import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any
import socketio
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger

# Import screen capture service
try:
    from app.services.screen_capture import ScreenCaptureService
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Screen capture not available: {e}")
    SCREEN_CAPTURE_AVAILABLE = False

# Configure logging
logger.remove()
logger.add("logs/app.log", rotation="10 MB", level="INFO")
logger.add(lambda msg: print(msg, end=""), level="INFO")

# Global services
ai_engine = None
audio_processor = None
conversation_analyzer = None
screen_capture = None

class CohereAIEngine:
    """AI Engine with Cohere integration"""
    def __init__(self):
        self.is_ready = False
        self.cohere_client = None
        
    async def initialize(self):
        """Initialize the AI engine with Cohere"""
        try:
            # Try to import and initialize Cohere
            import cohere
            
            # Check for API key in environment or use a placeholder
            import os
            api_key = os.getenv('COHERE_API_KEY', 'your-cohere-api-key-here')
            
            # For demo purposes, you can use a test key here
            # Replace 'demo-key' with your actual Cohere API key
            demo_key = 'NHlCa1jrvthkgsJZk4RJoSFXdF1HxE6mUe8YXdmx'  # Change this to your actual API key
            
            if api_key and api_key != 'your-cohere-api-key-here':
                self.cohere_client = cohere.Client(api_key)
                logger.info("✅ Cohere client initialized successfully")
                logger.info("🚀 AI responses will be powered by Cohere!")
            elif demo_key and demo_key != 'demo-key':
                self.cohere_client = cohere.Client(demo_key)
                logger.info("✅ Cohere client initialized with demo key")
                logger.info("🚀 AI responses will be powered by Cohere!")
            else:
                logger.warning("⚠️ No Cohere API key found. Using fallback responses.")
                logger.info("💡 To enable Cohere AI responses:")
                logger.info("   1. Run: python setup_cohere.py")
                logger.info("   2. Or set: $env:COHERE_API_KEY='your-api-key-here'")
                logger.info("   3. Or edit demo_key in working_app_with_cohere.py")
                self.cohere_client = None
                
            self.is_ready = True
            logger.info("✅ AI Engine initialized")
            
        except ImportError:
            logger.warning("⚠️ Cohere package not installed. Using fallback responses.")
            self.cohere_client = None
            self.is_ready = True
        except Exception as e:
            logger.error(f"❌ Error initializing AI Engine: {e}")
            self.cohere_client = None
            self.is_ready = True
    
    async def generate_response(self, message: str, context: str = "") -> str:
        """Generate AI response using Cohere"""
        try:
            if self.cohere_client:
                # Use Cohere Chat API (newer, recommended)
                try:
                    # Include context in the message for screen analysis
                    full_message = message
                    if context and any(word in message.lower() for word in ['screen', 'see', 'show', 'display', 'what', 'analyze', 'look']):
                        full_message = f"""Screen data: {context}

User: {message}

Give a concise response about what you see on their screen."""
                    elif context:
                        full_message = f"""You are Convo AI, a helpful assistant. You can see the user's screen but only mention it if relevant.

Screen context: {context}

User: {message}

Respond naturally to their question. Only mention screen details if they ask about it."""
                    
                    response = self.cohere_client.chat(
                        message=full_message,
                        model="command-r-plus",
                        max_tokens=80,
                        temperature=0.3,
                        chat_history=[]
                    )
                    
                    return response.text.strip()
                    
                except Exception as chat_error:
                    logger.warning(f"Chat API failed, trying Generate API: {chat_error}")
                    
                    # Fallback to Generate API if Chat API fails
                    if any(word in message.lower() for word in ['screen', 'see', 'show', 'display', 'what', 'analyze', 'look']):
                        prompt = f"""Screen data: {context}

User: {message}

Give a concise response about what you see on their screen."""
                    else:
                        prompt = f"""You are Convo AI, a helpful assistant. You can see the user's screen but only mention it if relevant.

Screen context: {context}

User: {message}

Respond naturally to their question. Only mention screen details if they ask about it."""

                    response = self.cohere_client.generate(
                        prompt=prompt,
                        model="command",
                        max_tokens=60,
                        temperature=0.3,
                        k=0,
                        p=0.75,
                        stop_sequences=["Human:", "User:"],
                        return_likelihoods="NONE"
                    )
                    
                    return response.generations[0].text.strip()
            else:
                # Fallback responses when Cohere is not available
                return self._get_fallback_response(message)
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_fallback_response(message)
    
    def _get_fallback_response(self, message: str) -> str:
        """Provide fallback responses when Cohere is not available"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your AI conversation assistant. How can I help you today?"
        elif any(word in message_lower for word in ['help', 'assist']):
            return "I'm here to help with your conversations! I can provide suggestions, analyze sentiment, and help you communicate more effectively."
        elif any(word in message_lower for word in ['thank', 'thanks']):
            return "You're welcome! I'm happy to help with your conversation needs."
        elif any(word in message_lower for word in ['bye', 'goodbye', 'see you']):
            return "Goodbye! Feel free to come back anytime you need conversation assistance."
        else:
            return f"I understand you said: '{message}'. I'm here to help with conversation analysis and suggestions. What would you like to discuss?"

class AudioProcessor:
    """Audio processing service with speech recognition"""
    def __init__(self):
        self.is_ready = False
        self.recognizer = None
        self.microphone = None
    
    async def initialize(self):
        """Initialize speech recognition"""
        try:
            import speech_recognition as sr
            import sounddevice as sd
            
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                logger.info("🎤 Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.is_ready = True
            logger.info("✅ Audio Processor initialized with speech recognition")
            
        except ImportError as e:
            logger.warning(f"⚠️ Speech recognition libraries not available: {e}")
            self.is_ready = True
        except Exception as e:
            logger.error(f"❌ Error initializing Audio Processor: {e}")
            self.is_ready = True
    
    async def cleanup(self):
        logger.info("✅ Audio Processor cleaned up")
    
    async def listen_for_speech(self, timeout=5, phrase_time_limit=10) -> str:
        """Listen for speech and return transcribed text"""
        if not self.is_ready or not self.recognizer or not self.microphone:
            return ""
        
        try:
            import speech_recognition as sr
            
            logger.info("🎤 Listening for speech...")
            
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            logger.info("🔄 Processing speech...")
            
            # Try Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(audio)
                logger.info(f"✅ Speech recognized: {text}")
                return text
            except sr.UnknownValueError:
                logger.warning("⚠️ Could not understand audio")
                return ""
            except sr.RequestError as e:
                logger.warning(f"⚠️ Google Speech Recognition error: {e}")
                # Try offline recognition as fallback
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    logger.info(f"✅ Speech recognized (offline): {text}")
                    return text
                except:
                    logger.warning("⚠️ Offline recognition also failed")
                    return ""
                    
        except sr.WaitTimeoutError:
            logger.info("⏰ Listening timeout - no speech detected")
            return ""
        except Exception as e:
            logger.error(f"❌ Error in speech recognition: {e}")
            return ""
    
    async def test_microphone(self) -> bool:
        """Test if microphone is working"""
        try:
            import sounddevice as sd
            
            # List available audio devices
            devices = sd.query_devices()
            logger.info(f"🎤 Available audio devices: {len(devices)}")
            
            # Test recording
            duration = 1  # seconds
            sample_rate = 44100
            
            logger.info("🎤 Testing microphone...")
            recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
            sd.wait()  # Wait until recording is finished
            
            # Check if we got any audio
            max_amplitude = max(abs(recording))
            if max_amplitude > 0.01:  # Threshold for detecting sound
                logger.info("✅ Microphone test successful")
                return True
            else:
                logger.warning("⚠️ Microphone test failed - no audio detected")
                return False
                
        except Exception as e:
            logger.error(f"❌ Microphone test failed: {e}")
            return False

class ConversationAnalyzer:
    """Conversation analysis service"""
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine
        self.is_ready = True
    
    async def initialize(self):
        logger.info("✅ Conversation Analyzer initialized")
    
    async def cleanup(self):
        logger.info("✅ Conversation Analyzer cleaned up")
    
    async def analyze_message(self, message: str) -> Dict[str, Any]:
        """Analyze a message for sentiment and insights"""
        try:
            # Simple sentiment analysis
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'horrible', 'worst']
            
            message_lower = message.lower()
            positive_count = sum(1 for word in positive_words if word in message_lower)
            negative_count = sum(1 for word in negative_words if word in message_lower)
            
            if positive_count > negative_count:
                sentiment = "positive"
            elif negative_count > positive_count:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "sentiment": sentiment,
                "confidence": 0.8,
                "key_words": [word for word in message.split() if len(word) > 4],
                "message_length": len(message),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing message: {e}")
            return {"sentiment": "neutral", "confidence": 0.5, "error": str(e)}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ai_engine, audio_processor, conversation_analyzer, screen_capture
    
    logger.info("🚀 Starting AI Conversation Assistant...")
    
    # Initialize services
    ai_engine = CohereAIEngine()
    await ai_engine.initialize()
    
    audio_processor = AudioProcessor()
    await audio_processor.initialize()
    
    conversation_analyzer = ConversationAnalyzer(ai_engine)
    await conversation_analyzer.initialize()
    
    # Initialize Screen Capture Service
    if SCREEN_CAPTURE_AVAILABLE:
        screen_capture = ScreenCaptureService()
        await screen_capture.initialize()
        logger.info("✅ Screen Capture Service initialized")
    else:
        logger.warning("⚠️ Screen Capture Service not available")
    
    logger.info("🎉 All services initialized successfully!")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down services...")
    if conversation_analyzer:
        await conversation_analyzer.cleanup()
    if audio_processor:
        await audio_processor.cleanup()
    if screen_capture:
        await screen_capture.cleanup()
    logger.info("✅ Cleanup completed")

# Create FastAPI app
app = FastAPI(
    title="AI Conversation Assistant",
    description="Real-time AI-powered conversation support and analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    logger=True,
    engineio_logger=True
)

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f"Client {sid} connected")
    await sio.emit('connected', {'message': 'Connected to AI Assistant'}, room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client {sid} disconnected")

@sio.event
async def user_message(sid, data):
    """Handle user messages and generate AI responses"""
    try:
        message = data.get('message', '')
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        logger.info(f"Received message from {sid}: {message}")
        
        # Analyze the message
        analysis = await conversation_analyzer.analyze_message(message)
        
        # Get screen context if available
        screen_context = ""
        if screen_capture and screen_capture.is_capturing:
            screen_summary = screen_capture.get_screen_summary()
            screen_context = f"Current screen analysis: {screen_summary}. "
            logger.info(f"📺 Including screen context: {screen_summary}")
        
        # Generate AI response with screen context
        context = f"{screen_context}Previous analysis: {analysis}"
        ai_response = await ai_engine.generate_response(message, context)
        
        # Send analysis back to client
        await sio.emit('message_analysis', {
            'message': message,
            'analysis': analysis,
            'timestamp': timestamp
        }, room=sid)
        
        # Send AI response
        await sio.emit('ai_response', {
            'response': ai_response,
            'timestamp': datetime.utcnow().isoformat()
        }, room=sid)
        
        logger.info(f"Sent AI response to {sid}: {ai_response}")
        
    except Exception as e:
        logger.error(f"Error handling user message: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

@sio.event
async def start_conversation(sid, data):
    """Handle conversation start"""
    try:
        conversation_type = data.get('type', 'meeting')
        platform = data.get('platform', 'desktop')
        
        conversation_id = f"conv_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        await sio.emit('conversation_started', {
            'conversation_id': conversation_id,
            'status': 'started',
            'message': 'Conversation started! I\'m ready to help with AI-powered suggestions.'
        }, room=sid)
        
        logger.info(f"Started conversation {conversation_id} for client {sid}")
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

@sio.event
async def end_conversation(sid, data):
    """Handle conversation end"""
    try:
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            await sio.emit('error', {'message': 'No conversation ID provided'}, room=sid)
            return
        
        await sio.emit('conversation_ended', {
            'conversation_id': conversation_id,
            'status': 'ended',
            'message': 'Conversation ended. Thank you for using AI Assistant!'
        }, room=sid)
        
        logger.info(f"Ended conversation {conversation_id} for client {sid}")
        
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Conversation Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "ai_engine": ai_engine.is_ready if ai_engine else False,
            "audio_processor": audio_processor.is_ready if audio_processor else False,
            "conversation_analyzer": conversation_analyzer.is_ready if conversation_analyzer else False
        }
    }

@app.get("/api/test")
async def test_api():
    """Test API endpoint"""
    return {
        "message": "API is working",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "ai_engine": "cohere" if ai_engine and ai_engine.cohere_client else "fallback",
            "audio_processor": "active" if audio_processor else "inactive",
            "conversation_analyzer": "active" if conversation_analyzer else "inactive"
        }
    }

@app.post("/api/chat")
async def chat_endpoint(data: dict):
    """Chat endpoint for testing AI responses"""
    try:
        message = data.get('message', '')
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get screen context if available
        screen_context = ""
        if screen_capture and screen_capture.is_capturing:
            screen_summary = screen_capture.get_screen_summary()
            screen_context = f"Current screen analysis: {screen_summary}. "
            logger.info(f"📺 Including screen context in chat: {screen_summary}")
        
        # Generate AI response with screen context
        ai_response = await ai_engine.generate_response(message, screen_context)
        
        return {
            "message": message,
            "response": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/speech/listen")
async def speech_listen_endpoint():
    """Listen for speech and return transcribed text"""
    try:
        if not audio_processor or not audio_processor.is_ready:
            raise HTTPException(status_code=503, detail="Audio processor not available")
        
        # Listen for speech
        transcribed_text = await audio_processor.listen_for_speech(timeout=10, phrase_time_limit=15)
        
        if not transcribed_text:
            return {
                "success": False,
                "message": "No speech detected or could not understand audio",
                "text": "",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "message": "Speech recognized successfully",
            "text": transcribed_text,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in speech recognition: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/speech/test")
async def speech_test_endpoint():
    """Test microphone functionality"""
    try:
        if not audio_processor:
            raise HTTPException(status_code=503, detail="Audio processor not available")
        
        # Test microphone
        mic_working = await audio_processor.test_microphone()
        
        return {
            "success": mic_working,
            "message": "Microphone test completed" if mic_working else "Microphone test failed",
            "microphone_working": mic_working,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in microphone test: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/speech/chat")
async def speech_chat_endpoint():
    """Listen for speech, transcribe, and get AI response"""
    try:
        if not audio_processor or not audio_processor.is_ready:
            raise HTTPException(status_code=503, detail="Audio processor not available")
        
        # Listen for speech
        transcribed_text = await audio_processor.listen_for_speech(timeout=10, phrase_time_limit=15)
        
        if not transcribed_text:
            return {
                "success": False,
                "message": "No speech detected or could not understand audio",
                "transcribed_text": "",
                "ai_response": "",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Generate AI response
        ai_response = await ai_engine.generate_response(transcribed_text)
        
        return {
            "success": True,
            "message": "Speech processed successfully",
            "transcribed_text": transcribed_text,
            "ai_response": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in speech chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Screen Capture Endpoints
@app.get("/api/screen/status")
async def screen_status():
    """Get screen capture status"""
    try:
        if not screen_capture:
            return {
                "available": False,
                "message": "Screen capture service not available",
                "is_capturing": False
            }
        
        return {
            "available": True,
            "is_capturing": screen_capture.is_capturing,
            "last_capture": screen_capture.last_capture_time,
            "message": "Screen capture service is ready"
        }
        
    except Exception as e:
        logger.error(f"Error getting screen status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/screen/start")
async def start_screen_capture():
    """Start screen capture"""
    try:
        if not screen_capture:
            raise HTTPException(status_code=503, detail="Screen capture service not available")
        
        await screen_capture.start_capture(interval=0.5)
        
        return {
            "success": True,
            "message": "Screen capture started",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting screen capture: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/screen/stop")
async def stop_screen_capture():
    """Stop screen capture"""
    try:
        if not screen_capture:
            raise HTTPException(status_code=503, detail="Screen capture service not available")
        
        await screen_capture.stop_capture()
        
        return {
            "success": True,
            "message": "Screen capture stopped",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping screen capture: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/screen/image")
async def get_screen_image():
    """Get current screen image as base64"""
    try:
        if not screen_capture:
            raise HTTPException(status_code=503, detail="Screen capture service not available")
        
        if not screen_capture.is_capturing:
            raise HTTPException(status_code=400, detail="Screen capture not started")
        
        image_base64 = screen_capture.get_screen_image_base64()
        
        if not image_base64:
            raise HTTPException(status_code=404, detail="No screen image available")
        
        return {
            "success": True,
            "image": image_base64,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting screen image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/screen/analysis")
async def get_screen_analysis():
    """Get current screen analysis"""
    try:
        if not screen_capture:
            raise HTTPException(status_code=503, detail="Screen capture service not available")
        
        analysis = screen_capture.get_screen_analysis()
        summary = screen_capture.get_screen_summary()
        
        return {
            "success": True,
            "analysis": analysis,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting screen analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/screen/chat")
async def screen_chat_endpoint(request: dict):
    """Get AI response based on screen content"""
    try:
        if not screen_capture:
            raise HTTPException(status_code=503, detail="Screen capture service not available")
        
        user_message = request.get("message", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get screen analysis
        screen_summary = screen_capture.get_screen_summary()
        
        # Create context with screen information
        context = f"Current screen analysis: {screen_summary}"
        
        # Get AI response with screen context
        ai_response = await ai_engine.generate_response(user_message, context)
        
        return {
            "success": True,
            "message": "Screen-based AI response generated",
            "user_message": user_message,
            "screen_summary": screen_summary,
            "ai_response": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in screen chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Combine FastAPI and Socket.IO
socket_app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    logger.info("🚀 Starting AI Conversation Assistant server...")
    uvicorn.run(
        socket_app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
