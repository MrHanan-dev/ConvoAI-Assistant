"""
Win Rate Analytics - Cluely.ai's signature analytics feature
Analyzes communication effectiveness, clarity, confidence, and impact
"""

import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from loguru import logger
import statistics

from app.services.ai_engine import AIEngine


@dataclass
class CommunicationMetrics:
    """Communication effectiveness metrics"""
    clarity_score: float  # 0-1 scale
    confidence_score: float  # 0-1 scale
    impact_score: float  # 0-1 scale
    engagement_score: float  # 0-1 scale
    persuasiveness_score: float  # 0-1 scale
    overall_score: float  # 0-1 scale


class WinRateAnalyzer:
    """Cluely.ai's win rate analytics engine"""
    
    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine
        self.conversation_metrics = {}
        self.historical_data = []
        
        # Communication effectiveness factors
        self.clarity_indicators = {
            "positive": [
                "clear", "understand", "makes sense", "got it", "I see",
                "that's helpful", "good point", "exactly", "right"
            ],
            "negative": [
                "confused", "unclear", "don't understand", "what do you mean",
                "can you explain", "I'm lost", "not following", "huh"
            ]
        }
        
        self.confidence_indicators = {
            "high_confidence": [
                "definitely", "absolutely", "certainly", "guaranteed", "proven",
                "without doubt", "confident", "sure", "positive"
            ],
            "low_confidence": [
                "maybe", "possibly", "might", "could be", "not sure",
                "think so", "probably", "perhaps", "potentially"
            ]
        }
        
        self.impact_indicators = {
            "high_impact": [
                "game changer", "revolutionary", "significant", "major improvement",
                "dramatic", "substantial", "transformative", "breakthrough"
            ],
            "engagement_signals": [
                "tell me more", "how does that work", "what about", "can you show",
                "interesting", "that sounds good", "I like that", "impressive"
            ]
        }
    
    async def analyze_conversation_effectiveness(
        self,
        conversation_id: str,
        transcript: str,
        audio_features: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> CommunicationMetrics:
        """Analyze communication effectiveness - Core Cluely.ai feature"""
        try:
            # Parallel analysis of different metrics
            tasks = [
                self._analyze_clarity(transcript, conversation_context),
                self._analyze_confidence(transcript, audio_features),
                self._analyze_impact(transcript, conversation_context),
                self._analyze_engagement(transcript, conversation_context),
                self._analyze_persuasiveness(transcript, conversation_context)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            clarity_score = results[0] if not isinstance(results[0], Exception) else 0.5
            confidence_score = results[1] if not isinstance(results[1], Exception) else 0.5
            impact_score = results[2] if not isinstance(results[2], Exception) else 0.5
            engagement_score = results[3] if not isinstance(results[3], Exception) else 0.5
            persuasiveness_score = results[4] if not isinstance(results[4], Exception) else 0.5
            
            # Calculate overall score with weighted average
            overall_score = (
                clarity_score * 0.25 +
                confidence_score * 0.20 +
                impact_score * 0.20 +
                engagement_score * 0.20 +
                persuasiveness_score * 0.15
            )
            
            metrics = CommunicationMetrics(
                clarity_score=clarity_score,
                confidence_score=confidence_score,
                impact_score=impact_score,
                engagement_score=engagement_score,
                persuasiveness_score=persuasiveness_score,
                overall_score=overall_score
            )
            
            # Store metrics
            self.conversation_metrics[conversation_id] = {
                "metrics": metrics,
                "timestamp": datetime.utcnow(),
                "transcript_length": len(transcript),
                "context": conversation_context
            }
            
            logger.info(f"Win rate analysis complete for {conversation_id}: {overall_score:.2f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing conversation effectiveness: {e}")
            return CommunicationMetrics(0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
    
    async def _analyze_clarity(self, transcript: str, context: Optional[Dict[str, Any]]) -> float:
        """Analyze communication clarity"""
        try:
            transcript_lower = transcript.lower()
            
            # Count clarity indicators
            positive_signals = sum(1 for indicator in self.clarity_indicators["positive"] 
                                 if indicator in transcript_lower)
            negative_signals = sum(1 for indicator in self.clarity_indicators["negative"] 
                                 if indicator in transcript_lower)
            
            # Calculate base clarity score
            if positive_signals + negative_signals == 0:
                base_score = 0.6  # Neutral if no signals
            else:
                base_score = positive_signals / (positive_signals + negative_signals)
            
            # Adjust for conversation factors
            word_count = len(transcript.split())
            
            # Penalty for overly long explanations (may indicate lack of clarity)
            if word_count > 500:
                length_penalty = min(0.2, (word_count - 500) / 2000)
                base_score -= length_penalty
            
            # Bonus for concise, clear communication
            if 50 < word_count < 200 and positive_signals > 0:
                base_score += 0.1
            
            # Use AI for deeper clarity analysis
            ai_clarity_score = await self._get_ai_clarity_score(transcript)
            
            # Combine scores
            final_score = (base_score * 0.6) + (ai_clarity_score * 0.4)
            
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            logger.error(f"Error analyzing clarity: {e}")
            return 0.5
    
    async def _analyze_confidence(self, transcript: str, audio_features: Optional[Dict[str, Any]]) -> float:
        """Analyze confidence level"""
        try:
            transcript_lower = transcript.lower()
            
            # Text-based confidence analysis
            high_confidence = sum(1 for indicator in self.confidence_indicators["high_confidence"] 
                                if indicator in transcript_lower)
            low_confidence = sum(1 for indicator in self.confidence_indicators["low_confidence"] 
                               if indicator in transcript_lower)
            
            # Calculate text confidence score
            if high_confidence + low_confidence == 0:
                text_score = 0.6
            else:
                text_score = high_confidence / (high_confidence + low_confidence)
            
            # Audio-based confidence analysis (if available)
            audio_score = 0.6  # Default
            if audio_features:
                # Analyze voice characteristics for confidence
                pitch_variance = audio_features.get("pitch_variance", 0.5)
                speaking_rate = audio_features.get("speaking_rate", 150)  # words per minute
                volume_consistency = audio_features.get("volume_consistency", 0.5)
                
                # Confident speakers tend to have:
                # - Moderate pitch variance (not monotone, not erratic)
                # - Steady speaking rate (120-180 wpm)
                # - Consistent volume
                
                pitch_score = 1.0 - abs(pitch_variance - 0.4)  # Optimal around 0.4
                rate_score = 1.0 - abs(speaking_rate - 150) / 100  # Optimal around 150 wpm
                volume_score = volume_consistency
                
                audio_score = (pitch_score + rate_score + volume_score) / 3
            
            # Combine text and audio scores
            final_score = (text_score * 0.7) + (audio_score * 0.3)
            
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            logger.error(f"Error analyzing confidence: {e}")
            return 0.5
    
    async def _analyze_impact(self, transcript: str, context: Optional[Dict[str, Any]]) -> float:
        """Analyze communication impact"""
        try:
            transcript_lower = transcript.lower()
            
            # Count impact indicators
            high_impact = sum(1 for indicator in self.impact_indicators["high_impact"] 
                            if indicator in transcript_lower)
            
            # Analyze for specific impact factors
            quantified_benefits = len([word for word in transcript_lower.split() 
                                     if any(char.isdigit() for char in word) and 
                                     any(benefit in transcript_lower for benefit in 
                                         ["save", "increase", "improve", "reduce", "boost"])])
            
            concrete_examples = transcript_lower.count("for example") + transcript_lower.count("such as")
            
            # Calculate impact score
            impact_factors = high_impact + (quantified_benefits * 2) + concrete_examples
            
            # Normalize to 0-1 scale
            base_score = min(1.0, impact_factors / 10.0)
            
            # Bonus for specific business outcomes mentioned
            business_outcomes = ["roi", "revenue", "profit", "efficiency", "productivity", "cost savings"]
            outcome_bonus = sum(0.1 for outcome in business_outcomes if outcome in transcript_lower)
            
            final_score = min(1.0, base_score + outcome_bonus)
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error analyzing impact: {e}")
            return 0.5
    
    async def _analyze_engagement(self, transcript: str, context: Optional[Dict[str, Any]]) -> float:
        """Analyze audience engagement"""
        try:
            transcript_lower = transcript.lower()
            
            # Count engagement signals
            engagement_signals = sum(1 for signal in self.impact_indicators["engagement_signals"] 
                                   if signal in transcript_lower)
            
            # Analyze question patterns
            questions_asked = transcript.count("?")
            follow_up_questions = sum(1 for phrase in ["what about", "how about", "what if"] 
                                    if phrase in transcript_lower)
            
            # Interactive elements
            interactive_phrases = ["let me show you", "take a look", "notice how", "see this"]
            interactivity = sum(1 for phrase in interactive_phrases if phrase in transcript_lower)
            
            # Calculate engagement score
            engagement_factors = engagement_signals + (questions_asked * 0.5) + follow_up_questions + interactivity
            
            # Normalize to 0-1 scale
            base_score = min(1.0, engagement_factors / 15.0)
            
            # Context-based adjustments
            if context:
                conversation_length = context.get("duration_seconds", 0)
                if conversation_length > 300:  # 5+ minute conversations
                    if engagement_factors > 5:
                        base_score += 0.1  # Bonus for sustained engagement
            
            return max(0.0, min(1.0, base_score))
            
        except Exception as e:
            logger.error(f"Error analyzing engagement: {e}")
            return 0.5
    
    async def _analyze_persuasiveness(self, transcript: str, context: Optional[Dict[str, Any]]) -> float:
        """Analyze persuasiveness of communication"""
        try:
            transcript_lower = transcript.lower()
            
            # Persuasion techniques
            persuasion_techniques = {
                "social_proof": ["others", "clients", "customers", "companies like yours"],
                "authority": ["expert", "proven", "research shows", "studies indicate"],
                "scarcity": ["limited", "exclusive", "only", "few remaining"],
                "reciprocity": ["help you", "for you", "benefit", "value"],
                "commitment": ["agree", "commit", "promise", "guarantee"]
            }
            
            technique_score = 0
            for technique, phrases in persuasion_techniques.items():
                technique_count = sum(1 for phrase in phrases if phrase in transcript_lower)
                technique_score += min(1.0, technique_count / 3.0)  # Max 1 point per technique
            
            # Normalize technique score
            technique_score = technique_score / len(persuasion_techniques)
            
            # Emotional appeal
            emotional_words = ["feel", "imagine", "picture", "experience", "excited", "confident"]
            emotional_score = min(1.0, sum(1 for word in emotional_words if word in transcript_lower) / 5.0)
            
            # Logical structure
            logical_connectors = ["because", "therefore", "as a result", "that's why", "so"]
            logical_score = min(1.0, sum(1 for connector in logical_connectors if connector in transcript_lower) / 3.0)
            
            # Combine scores
            final_score = (technique_score * 0.5) + (emotional_score * 0.25) + (logical_score * 0.25)
            
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            logger.error(f"Error analyzing persuasiveness: {e}")
            return 0.5
    
    async def _get_ai_clarity_score(self, transcript: str) -> float:
        """Use AI to assess communication clarity"""
        try:
            prompt = f"""
            Analyze the clarity of this communication on a scale of 0-1:
            
            "{transcript[:500]}"
            
            Consider:
            - How easy is it to understand?
            - Are concepts explained clearly?
            - Is the language appropriate for the audience?
            - Are there any confusing or ambiguous statements?
            
            Return only a number between 0 and 1.
            """
            
            response = await self.ai_engine.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert communication analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            return float(score_text)
            
        except Exception as e:
            logger.error(f"Error getting AI clarity score: {e}")
            return 0.6
    
    async def get_win_rate_prediction(self, conversation_id: str) -> Dict[str, Any]:
        """Get win rate prediction based on communication metrics"""
        try:
            if conversation_id not in self.conversation_metrics:
                return {"prediction": 0.5, "confidence": 0.0, "factors": []}
            
            metrics = self.conversation_metrics[conversation_id]["metrics"]
            
            # Win rate prediction algorithm (based on Cluely.ai methodology)
            base_prediction = metrics.overall_score
            
            # Adjust based on specific factors
            adjustments = []
            
            # High clarity and confidence boost win rate
            if metrics.clarity_score > 0.8 and metrics.confidence_score > 0.8:
                base_prediction += 0.1
                adjustments.append("High clarity and confidence detected")
            
            # High engagement is a strong predictor
            if metrics.engagement_score > 0.7:
                base_prediction += 0.15
                adjustments.append("Strong audience engagement")
            
            # Impact and persuasiveness combination
            if metrics.impact_score > 0.6 and metrics.persuasiveness_score > 0.6:
                base_prediction += 0.1
                adjustments.append("Effective impact and persuasion")
            
            # Cap at 0.95 (never 100% certain)
            final_prediction = min(0.95, base_prediction)
            
            # Calculate confidence in prediction
            score_variance = np.var([
                metrics.clarity_score,
                metrics.confidence_score, 
                metrics.impact_score,
                metrics.engagement_score,
                metrics.persuasiveness_score
            ])
            
            confidence = 1.0 - score_variance  # Lower variance = higher confidence
            
            return {
                "prediction": final_prediction,
                "confidence": confidence,
                "factors": adjustments,
                "metrics_breakdown": {
                    "clarity": metrics.clarity_score,
                    "confidence": metrics.confidence_score,
                    "impact": metrics.impact_score,
                    "engagement": metrics.engagement_score,
                    "persuasiveness": metrics.persuasiveness_score,
                    "overall": metrics.overall_score
                },
                "recommendation": self._get_improvement_recommendation(metrics)
            }
            
        except Exception as e:
            logger.error(f"Error calculating win rate prediction: {e}")
            return {"prediction": 0.5, "confidence": 0.0, "factors": []}
    
    def _get_improvement_recommendation(self, metrics: CommunicationMetrics) -> str:
        """Get personalized improvement recommendation"""
        try:
            # Find the lowest scoring metric
            scores = {
                "clarity": metrics.clarity_score,
                "confidence": metrics.confidence_score,
                "impact": metrics.impact_score,
                "engagement": metrics.engagement_score,
                "persuasiveness": metrics.persuasiveness_score
            }
            
            lowest_metric = min(scores.items(), key=lambda x: x[1])
            
            recommendations = {
                "clarity": "Focus on clearer explanations. Use simpler language and check for understanding more frequently.",
                "confidence": "Speak with more certainty. Use definitive language and avoid hesitant phrases like 'maybe' or 'I think'.",
                "impact": "Emphasize concrete benefits and quantifiable outcomes. Use specific examples and case studies.",
                "engagement": "Ask more questions and encourage interaction. Use phrases like 'What do you think?' and 'How does this sound?'",
                "persuasiveness": "Incorporate more persuasion techniques like social proof, authority, and emotional appeals."
            }
            
            return recommendations.get(lowest_metric[0], "Continue with your current approach - it's working well!")
            
        except Exception as e:
            logger.error(f"Error generating improvement recommendation: {e}")
            return "Focus on maintaining clear, confident communication."
    
    async def get_historical_trends(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get historical win rate trends"""
        try:
            # This would typically query the database for historical data
            # For now, return mock trend data
            
            dates = []
            win_rates = []
            
            for i in range(days):
                date = datetime.utcnow() - timedelta(days=i)
                dates.append(date.isoformat())
                # Mock trend - gradually improving win rate
                base_rate = 0.6 + (i / days) * 0.2
                win_rates.append(base_rate + np.random.normal(0, 0.05))
            
            return {
                "dates": dates[::-1],  # Reverse to chronological order
                "win_rates": win_rates[::-1],
                "average_win_rate": np.mean(win_rates),
                "trend": "improving" if win_rates[-1] > win_rates[0] else "declining",
                "improvement_rate": (win_rates[-1] - win_rates[0]) / days
            }
            
        except Exception as e:
            logger.error(f"Error getting historical trends: {e}")
            return {"dates": [], "win_rates": [], "average_win_rate": 0.5}
