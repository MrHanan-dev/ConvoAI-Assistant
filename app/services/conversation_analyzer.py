"""
Conversation analyzer for real-time analysis and insights
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import numpy as np
from loguru import logger

from app.services.ai_engine import AIEngine


class ConversationAnalyzer:
    """Real-time conversation analyzer"""
    
    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine
        self.is_ready = False
        
        # Analysis state
        self.active_conversations = {}  # conversation_id -> analysis state
        self.analysis_buffer = defaultdict(deque)  # Rolling buffer for analysis
        self.speaker_metrics = defaultdict(dict)  # Speaker-specific metrics
        
        # Analysis settings
        self.analysis_window = 30  # seconds
        self.min_analysis_interval = 5  # seconds between analyses
        
    async def initialize(self):
        """Initialize conversation analyzer"""
        try:
            logger.info("Initializing Conversation Analyzer...")
            
            # Ensure AI engine is ready
            if not self.ai_engine.is_ready:
                raise ValueError("AI Engine must be initialized first")
            
            self.is_ready = True
            logger.success("Conversation Analyzer initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize Conversation Analyzer: {e}")
            raise
    
    async def start_conversation_analysis(
        self,
        conversation_id: str,
        context: Dict[str, Any] = None
    ):
        """Start analyzing a conversation"""
        try:
            self.active_conversations[conversation_id] = {
                'started_at': datetime.utcnow(),
                'context': context or {},
                'last_analysis': None,
                'total_chunks': 0,
                'speakers': set(),
                'sentiment_history': [],
                'engagement_history': [],
                'objections': [],
                'suggestions_given': []
            }
            
            logger.info(f"Started analysis for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error starting conversation analysis: {e}")
    
    async def analyze_speech_chunk(
        self,
        conversation_id: str,
        text: str,
        speaker: str,
        timestamp: datetime,
        audio_features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze a chunk of speech in real-time"""
        try:
            if conversation_id not in self.active_conversations:
                await self.start_conversation_analysis(conversation_id)
            
            conv_state = self.active_conversations[conversation_id]
            
            # Update conversation state
            conv_state['total_chunks'] += 1
            conv_state['speakers'].add(speaker)
            
            # Perform AI analysis
            analysis = await self.ai_engine.analyze_conversation_chunk(
                text=text,
                speaker=speaker,
                timestamp=timestamp,
                conversation_id=conversation_id,
                context=conv_state['context']
            )
            
            # Update analysis history
            self._update_analysis_history(conversation_id, analysis)
            
            # Calculate aggregate metrics
            aggregate_metrics = self._calculate_aggregate_metrics(conversation_id)
            
            # Combine analysis with aggregate metrics
            full_analysis = {
                **analysis,
                'aggregate_metrics': aggregate_metrics,
                'conversation_stats': self._get_conversation_stats(conversation_id)
            }
            
            # Store in buffer for trend analysis
            self.analysis_buffer[conversation_id].append({
                'timestamp': timestamp,
                'analysis': full_analysis
            })
            
            # Keep buffer size manageable
            if len(self.analysis_buffer[conversation_id]) > 100:
                self.analysis_buffer[conversation_id].popleft()
            
            conv_state['last_analysis'] = timestamp
            
            logger.debug(f"Analyzed speech chunk for conversation {conversation_id}")
            return full_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing speech chunk: {e}")
            return {"error": str(e)}
    
    def _update_analysis_history(self, conversation_id: str, analysis: Dict[str, Any]):
        """Update analysis history for trend tracking"""
        try:
            conv_state = self.active_conversations[conversation_id]
            
            # Update sentiment history
            sentiment = analysis.get('sentiment', {})
            if sentiment:
                conv_state['sentiment_history'].append({
                    'timestamp': analysis.get('timestamp'),
                    'overall': sentiment.get('overall'),
                    'confidence': sentiment.get('confidence', 0),
                    'valence': sentiment.get('valence', 0)
                })
            
            # Update engagement history
            engagement = analysis.get('engagement', {})
            if engagement:
                conv_state['engagement_history'].append({
                    'timestamp': analysis.get('timestamp'),
                    'score': engagement.get('score', 0),
                    'speaker': analysis.get('speaker')
                })
            
            # Update objections
            objections = analysis.get('objections', [])
            for objection in objections:
                conv_state['objections'].append({
                    **objection,
                    'timestamp': analysis.get('timestamp')
                })
            
            # Update suggestions
            suggestions = analysis.get('suggestions', [])
            if suggestions:
                conv_state['suggestions_given'].extend(suggestions)
            
            # Keep history manageable
            max_history = 50
            if len(conv_state['sentiment_history']) > max_history:
                conv_state['sentiment_history'] = conv_state['sentiment_history'][-max_history:]
            if len(conv_state['engagement_history']) > max_history:
                conv_state['engagement_history'] = conv_state['engagement_history'][-max_history:]
            
        except Exception as e:
            logger.error(f"Error updating analysis history: {e}")
    
    def _calculate_aggregate_metrics(self, conversation_id: str) -> Dict[str, Any]:
        """Calculate aggregate metrics for the conversation"""
        try:
            conv_state = self.active_conversations[conversation_id]
            
            # Calculate average sentiment
            sentiment_history = conv_state['sentiment_history']
            avg_sentiment = {
                'overall': 'neutral',
                'confidence': 0.0,
                'valence': 0.0,
                'trend': 'stable'
            }
            
            if sentiment_history:
                valences = [s['valence'] for s in sentiment_history if s['valence'] is not None]
                if valences:
                    avg_sentiment['valence'] = np.mean(valences)
                    avg_sentiment['confidence'] = np.mean([s['confidence'] for s in sentiment_history])
                    
                    # Determine overall sentiment from valence
                    if avg_sentiment['valence'] > 0.1:
                        avg_sentiment['overall'] = 'positive'
                    elif avg_sentiment['valence'] < -0.1:
                        avg_sentiment['overall'] = 'negative'
                    
                    # Calculate trend
                    if len(valences) >= 3:
                        recent_trend = np.mean(valences[-3:]) - np.mean(valences[:-3])
                        if recent_trend > 0.1:
                            avg_sentiment['trend'] = 'improving'
                        elif recent_trend < -0.1:
                            avg_sentiment['trend'] = 'declining'
            
            # Calculate average engagement
            engagement_history = conv_state['engagement_history']
            avg_engagement = {
                'overall_score': 0.0,
                'user_engagement': 0.0,
                'prospect_engagement': 0.0,
                'balance': 'balanced'
            }
            
            if engagement_history:
                all_scores = [e['score'] for e in engagement_history]
                avg_engagement['overall_score'] = np.mean(all_scores)
                
                user_scores = [e['score'] for e in engagement_history if e['speaker'] == 'user']
                prospect_scores = [e['score'] for e in engagement_history if e['speaker'] != 'user']
                
                if user_scores:
                    avg_engagement['user_engagement'] = np.mean(user_scores)
                if prospect_scores:
                    avg_engagement['prospect_engagement'] = np.mean(prospect_scores)
                
                # Determine balance
                if avg_engagement['user_engagement'] > avg_engagement['prospect_engagement'] * 1.5:
                    avg_engagement['balance'] = 'user_dominated'
                elif avg_engagement['prospect_engagement'] > avg_engagement['user_engagement'] * 1.5:
                    avg_engagement['balance'] = 'prospect_dominated'
            
            # Objection analysis
            objections = conv_state['objections']
            objection_analysis = {
                'total_count': len(objections),
                'types': defaultdict(int),
                'urgency_distribution': defaultdict(int),
                'recent_objections': []
            }
            
            for objection in objections:
                objection_analysis['types'][objection.get('type', 'unknown')] += 1
                objection_analysis['urgency_distribution'][objection.get('urgency', 'medium')] += 1
            
            # Recent objections (last 5 minutes)
            recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
            objection_analysis['recent_objections'] = [
                obj for obj in objections
                if datetime.fromisoformat(obj['timestamp'].replace('Z', '+00:00')) > recent_cutoff
            ]
            
            return {
                'sentiment': avg_sentiment,
                'engagement': avg_engagement,
                'objections': dict(objection_analysis),
                'conversation_flow': self._analyze_conversation_flow(conversation_id)
            }
            
        except Exception as e:
            logger.error(f"Error calculating aggregate metrics: {e}")
            return {}
    
    def _analyze_conversation_flow(self, conversation_id: str) -> Dict[str, Any]:
        """Analyze conversation flow and pacing"""
        try:
            buffer = self.analysis_buffer[conversation_id]
            if len(buffer) < 2:
                return {'status': 'insufficient_data'}
            
            # Calculate speaking time distribution
            speaker_times = defaultdict(float)
            total_time = 0
            
            for i in range(1, len(buffer)):
                prev_entry = buffer[i-1]
                curr_entry = buffer[i]
                
                time_diff = (curr_entry['timestamp'] - prev_entry['timestamp']).total_seconds()
                speaker = prev_entry['analysis'].get('speaker', 'unknown')
                
                speaker_times[speaker] += time_diff
                total_time += time_diff
            
            # Calculate percentages
            speaker_percentages = {}
            for speaker, time_spent in speaker_times.items():
                speaker_percentages[speaker] = (time_spent / total_time * 100) if total_time > 0 else 0
            
            # Analyze pacing
            recent_entries = list(buffer)[-10:]  # Last 10 entries
            if len(recent_entries) >= 2:
                intervals = []
                for i in range(1, len(recent_entries)):
                    interval = (recent_entries[i]['timestamp'] - recent_entries[i-1]['timestamp']).total_seconds()
                    intervals.append(interval)
                
                avg_interval = np.mean(intervals)
                pacing = 'normal'
                if avg_interval < 3:
                    pacing = 'fast'
                elif avg_interval > 10:
                    pacing = 'slow'
            else:
                pacing = 'unknown'
            
            return {
                'status': 'analyzed',
                'speaker_time_distribution': speaker_percentages,
                'total_duration_seconds': total_time,
                'pacing': pacing,
                'turn_taking_balance': self._calculate_turn_balance(speaker_percentages)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing conversation flow: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_turn_balance(self, speaker_percentages: Dict[str, float]) -> str:
        """Calculate turn-taking balance"""
        if not speaker_percentages:
            return 'unknown'
        
        values = list(speaker_percentages.values())
        if len(values) < 2:
            return 'single_speaker'
        
        # Calculate coefficient of variation
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if mean_val == 0:
            return 'no_speech'
        
        cv = std_val / mean_val
        
        if cv < 0.3:
            return 'balanced'
        elif cv < 0.7:
            return 'slightly_unbalanced'
        else:
            return 'heavily_unbalanced'
    
    def _get_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """Get basic conversation statistics"""
        try:
            conv_state = self.active_conversations[conversation_id]
            duration = datetime.utcnow() - conv_state['started_at']
            
            return {
                'duration_seconds': duration.total_seconds(),
                'total_chunks': conv_state['total_chunks'],
                'unique_speakers': len(conv_state['speakers']),
                'suggestions_given': len(conv_state['suggestions_given']),
                'objections_detected': len(conv_state['objections'])
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation stats: {e}")
            return {}
    
    async def end_conversation_analysis(self, conversation_id: str) -> Dict[str, Any]:
        """End conversation analysis and return final summary"""
        try:
            if conversation_id not in self.active_conversations:
                return {'error': 'Conversation not found'}
            
            conv_state = self.active_conversations[conversation_id]
            
            # Generate final analysis
            final_analysis = {
                'conversation_id': conversation_id,
                'duration': (datetime.utcnow() - conv_state['started_at']).total_seconds(),
                'final_metrics': self._calculate_aggregate_metrics(conversation_id),
                'conversation_stats': self._get_conversation_stats(conversation_id),
                'summary': await self._generate_conversation_summary(conversation_id)
            }
            
            # Cleanup
            del self.active_conversations[conversation_id]
            if conversation_id in self.analysis_buffer:
                del self.analysis_buffer[conversation_id]
            
            logger.info(f"Ended analysis for conversation {conversation_id}")
            return final_analysis
            
        except Exception as e:
            logger.error(f"Error ending conversation analysis: {e}")
            return {'error': str(e)}
    
    async def _generate_conversation_summary(self, conversation_id: str) -> str:
        """Generate AI-powered conversation summary"""
        try:
            conv_state = self.active_conversations[conversation_id]
            buffer = self.analysis_buffer[conversation_id]
            
            # Extract key points from the conversation
            key_points = []
            objections = conv_state['objections']
            suggestions = conv_state['suggestions_given']
            
            # Build summary prompt
            summary_data = {
                'duration_minutes': (datetime.utcnow() - conv_state['started_at']).total_seconds() / 60,
                'speakers': list(conv_state['speakers']),
                'objections_count': len(objections),
                'suggestions_count': len(suggestions),
                'final_sentiment': self._calculate_aggregate_metrics(conversation_id).get('sentiment', {}).get('overall', 'neutral')
            }
            
            # Generate summary using AI
            summary = f"""
            Conversation Summary:
            - Duration: {summary_data['duration_minutes']:.1f} minutes
            - Participants: {', '.join(summary_data['speakers'])}
            - Objections detected: {summary_data['objections_count']}
            - AI suggestions provided: {summary_data['suggestions_count']}
            - Overall sentiment: {summary_data['final_sentiment']}
            """
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return "Summary generation failed"
    
    async def get_real_time_insights(self, conversation_id: str) -> Dict[str, Any]:
        """Get real-time insights for active conversation"""
        try:
            if conversation_id not in self.active_conversations:
                return {'error': 'Conversation not found'}
            
            return {
                'conversation_id': conversation_id,
                'is_active': True,
                'aggregate_metrics': self._calculate_aggregate_metrics(conversation_id),
                'conversation_stats': self._get_conversation_stats(conversation_id),
                'recent_trends': self._get_recent_trends(conversation_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time insights: {e}")
            return {'error': str(e)}
    
    def _get_recent_trends(self, conversation_id: str) -> Dict[str, Any]:
        """Get recent trends in the conversation"""
        try:
            buffer = self.analysis_buffer[conversation_id]
            if len(buffer) < 5:
                return {'status': 'insufficient_data'}
            
            recent_entries = list(buffer)[-5:]  # Last 5 entries
            
            # Sentiment trend
            sentiments = []
            for entry in recent_entries:
                sentiment = entry['analysis'].get('sentiment', {})
                if sentiment.get('valence') is not None:
                    sentiments.append(sentiment['valence'])
            
            sentiment_trend = 'stable'
            if len(sentiments) >= 3:
                if sentiments[-1] > sentiments[0] + 0.1:
                    sentiment_trend = 'improving'
                elif sentiments[-1] < sentiments[0] - 0.1:
                    sentiment_trend = 'declining'
            
            # Engagement trend
            engagements = []
            for entry in recent_entries:
                engagement = entry['analysis'].get('engagement', {})
                if engagement.get('score') is not None:
                    engagements.append(engagement['score'])
            
            engagement_trend = 'stable'
            if len(engagements) >= 3:
                if engagements[-1] > engagements[0] + 0.1:
                    engagement_trend = 'increasing'
                elif engagements[-1] < engagements[0] - 0.1:
                    engagement_trend = 'decreasing'
            
            return {
                'status': 'analyzed',
                'sentiment_trend': sentiment_trend,
                'engagement_trend': engagement_trend,
                'recent_objections': len([
                    entry for entry in recent_entries
                    if entry['analysis'].get('objections')
                ])
            }
            
        except Exception as e:
            logger.error(f"Error getting recent trends: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def cleanup(self):
        """Cleanup conversation analyzer"""
        try:
            self.active_conversations.clear()
            self.analysis_buffer.clear()
            self.speaker_metrics.clear()
            self.is_ready = False
            
            logger.info("Conversation Analyzer cleaned up")
            
        except Exception as e:
            logger.error(f"Error during conversation analyzer cleanup: {e}")
