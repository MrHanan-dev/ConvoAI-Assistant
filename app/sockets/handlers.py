"""
Socket.IO event handlers for real-time communication
"""

import asyncio
import json
from typing import Dict, Any
from datetime import datetime
from loguru import logger
import socketio


def register_socket_handlers(sio: socketio.AsyncServer):
    """Register all Socket.IO event handlers"""
    
    @sio.event
    async def connect(sid, environ):
        """Handle client connection"""
        logger.info(f"Client connected: {sid}")
        await sio.emit('connected', {'status': 'connected'}, room=sid)
    
    @sio.event
    async def disconnect(sid):
        """Handle client disconnection"""
        logger.info(f"Client disconnected: {sid}")
    
    @sio.event
    async def speech_detected(sid, data):
        """Handle speech detection from desktop client"""
        try:
            conversation_id = data.get('conversation_id')
            text = data.get('text', '')
            speaker = data.get('speaker', 'unknown')
            timestamp_str = data.get('timestamp')
            
            if not conversation_id or not text:
                await sio.emit('error', {'message': 'Invalid speech data'}, room=sid)
                return
            
            # Parse timestamp
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.utcnow()
            
            logger.info(f"Speech detected in conversation {conversation_id}: {text[:50]}...")
            
            # Process speech with AI engine
            from main import ai_engine, conversation_analyzer
            
            if ai_engine and conversation_analyzer:
                # Real AI analysis
                analysis = await conversation_analyzer.analyze_speech_chunk(
                    conversation_id=conversation_id,
                    text=text,
                    speaker=speaker,
                    timestamp=timestamp
                )
            else:
                # Fallback mock analysis
                analysis = {
                'conversation_id': conversation_id,
                'timestamp': timestamp.isoformat(),
                'speaker': speaker,
                'text': text,
                'sentiment': {
                    'overall': 'neutral',
                    'confidence': 0.7,
                    'valence': 0.0
                },
                'suggestions': [
                    {
                        'type': 'response',
                        'text': 'That\'s a great point. Can you tell me more about your specific requirements?',
                        'confidence': 0.8
                    }
                ] if speaker != 'user' else [],
                'objections': [],
                'engagement': {
                    'score': 0.6,
                    'speaker': speaker
                }
            }
            
            # Send analysis back to client
            await sio.emit('conversation_analysis', {'analysis': analysis}, room=sid)
            
            # Send AI suggestions if any
            if analysis['suggestions']:
                await sio.emit('ai_suggestion', {
                    'conversation_id': conversation_id,
                    'suggestions': analysis['suggestions']
                }, room=sid)
            
            # Check for objections
            if 'expensive' in text.lower() or 'cost' in text.lower():
                objection = {
                    'type': 'price',
                    'category': 'pricing',
                    'urgency': 'high',
                    'confidence': 0.9
                }
                responses = [
                    'I understand budget is important. Let me show you the ROI calculation...',
                    'What if we could structure this to fit your budget?'
                ]
                
                await sio.emit('objection_detected', {
                    'objection': objection,
                    'suggested_responses': responses
                }, room=sid)
            
        except Exception as e:
            logger.error(f"Error handling speech detection: {e}")
            await sio.emit('error', {'message': str(e)}, room=sid)
    
    @sio.event
    async def start_conversation(sid, data):
        """Handle conversation start"""
        try:
            conversation_type = data.get('type', 'meeting')
            platform = data.get('platform', 'desktop')
            
            # TODO: Create conversation in database
            conversation_id = f"conv_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            await sio.emit('conversation_started', {
                'conversation_id': conversation_id,
                'status': 'started'
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
            
            # TODO: End conversation analysis and save results
            
            await sio.emit('conversation_ended', {
                'conversation_id': conversation_id,
                'status': 'ended'
            }, room=sid)
            
            logger.info(f"Ended conversation {conversation_id} for client {sid}")
            
        except Exception as e:
            logger.error(f"Error ending conversation: {e}")
            await sio.emit('error', {'message': str(e)}, room=sid)
    
    @sio.event
    async def get_suggestions(sid, data):
        """Handle request for AI suggestions"""
        try:
            conversation_id = data.get('conversation_id')
            context = data.get('context', {})
            
            # Generate AI suggestions based on context
            from main import ai_engine
            
            if ai_engine and ai_engine.teleprompter:
                # Get teleprompter suggestions
                teleprompter_data = await ai_engine.teleprompter.process_conversation_update(
                    text="", 
                    speaker="user", 
                    conversation_context=context
                )
                suggestions = teleprompter_data.get("prompts", [])
            else:
                # Fallback suggestions
                suggestions = [
                    {
                        'type': 'question',
                        'text': 'What are your main priorities for this quarter?',
                        'confidence': 0.8
                    },
                    {
                        'type': 'response',
                        'text': 'Based on what you\'ve shared, it sounds like efficiency is key for your team.',
                        'confidence': 0.7
                    }
                ]
            
            await sio.emit('ai_suggestion', {
                'conversation_id': conversation_id,
                'suggestions': suggestions
            }, room=sid)
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            await sio.emit('error', {'message': str(e)}, room=sid)
    
    @sio.event
    async def rate_suggestion(sid, data):
        """Handle suggestion rating"""
        try:
            suggestion_id = data.get('suggestion_id')
            rating = data.get('rating')  # positive/negative
            
            # TODO: Store rating for ML improvement
            
            logger.info(f"Suggestion {suggestion_id} rated as {rating}")
            
        except Exception as e:
            logger.error(f"Error rating suggestion: {e}")
    
    @sio.event
    async def request_document_search(sid, data):
        """Handle document search request"""
        try:
            query = data.get('query', '')
            conversation_id = data.get('conversation_id')
            
            # Search documents using vector store
            from main import ai_engine
            
            if ai_engine and ai_engine.vector_store:
                # Real document search
                results = await ai_engine.vector_store.search_similar(
                    query=query,
                    limit=5,
                    threshold=0.6
                )
            else:
                # Fallback results
                results = [
                    {
                        'id': 'doc_1',
                        'title': 'Product Features Overview',
                        'snippet': 'Our platform includes advanced analytics...',
                        'relevance': 0.9
                    }
                ]
            
            await sio.emit('document_search_results', {
                'conversation_id': conversation_id,
                'query': query,
                'results': results
            }, room=sid)
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            await sio.emit('error', {'message': str(e)}, room=sid)
    
    @sio.event
    async def update_conversation_context(sid, data):
        """Handle conversation context updates"""
        try:
            conversation_id = data.get('conversation_id')
            context = data.get('context', {})
            
            # TODO: Update conversation context in analyzer
            
            logger.info(f"Updated context for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error updating conversation context: {e}")
    
    logger.info("Socket.IO handlers registered successfully")
