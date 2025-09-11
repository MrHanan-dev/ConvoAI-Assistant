"""
Adaptive AI Teleprompter - Core Cluely.ai Feature
Real-time adaptive prompts and talk tracks that adjust based on conversation flow
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import json

from app.services.ai_engine import AIEngine
from app.core.config import settings


class AdaptiveTeleprompter:
    """Cluely.ai's signature adaptive teleprompter feature"""
    
    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine
        self.is_active = False
        
        # Teleprompter state
        self.current_talk_track = None
        self.conversation_stage = "opening"  # opening, discovery, presentation, objection_handling, closing
        self.active_prompts = []
        self.prompt_history = []
        
        # Talk track templates (Cluely.ai style)
        self.talk_tracks = {
            "sales_discovery": {
                "stages": [
                    {
                        "name": "opening",
                        "prompts": [
                            "Start with a warm greeting and thank them for their time",
                            "Mention something specific about their company or recent news",
                            "Set the agenda: 'I'd love to learn about your current challenges and see if we can help'"
                        ],
                        "next_stage_triggers": ["tell me about", "what are your", "challenges", "goals"]
                    },
                    {
                        "name": "discovery", 
                        "prompts": [
                            "Ask: 'What's your biggest challenge with [their industry/role]?'",
                            "Follow up: 'How is that impacting your team/revenue?'",
                            "Dig deeper: 'What have you tried so far to solve this?'"
                        ],
                        "next_stage_triggers": ["we've tried", "currently using", "looking for solution"]
                    },
                    {
                        "name": "presentation",
                        "prompts": [
                            "Based on what you've shared, here's how we can help...",
                            "Let me show you exactly how this addresses your [specific challenge]",
                            "This is particularly relevant for companies like yours because..."
                        ],
                        "next_stage_triggers": ["sounds good", "how much", "pricing", "but what about"]
                    },
                    {
                        "name": "objection_handling",
                        "prompts": [
                            "I completely understand that concern. Many of our clients initially felt the same way",
                            "Let me address that specifically...",
                            "What would need to be true for this to work for you?"
                        ],
                        "next_stage_triggers": ["makes sense", "that helps", "okay"]
                    },
                    {
                        "name": "closing",
                        "prompts": [
                            "Based on everything we've discussed, it sounds like this could be a great fit",
                            "What questions do you have before we move forward?",
                            "What would be the next step from your perspective?"
                        ],
                        "next_stage_triggers": ["next steps", "move forward", "get started"]
                    }
                ]
            },
            "demo_call": {
                "stages": [
                    {
                        "name": "demo_opening",
                        "prompts": [
                            "Before I show you the platform, remind me of your main use case",
                            "I'll focus the demo on the features most relevant to your needs",
                            "Feel free to interrupt with questions as we go"
                        ]
                    },
                    {
                        "name": "feature_showcase",
                        "prompts": [
                            "This feature directly solves the [problem] you mentioned",
                            "Notice how this saves you [time/money] compared to your current process",
                            "Your team would use this daily for [specific use case]"
                        ]
                    }
                ]
            },
            "follow_up_call": {
                "stages": [
                    {
                        "name": "recap",
                        "prompts": [
                            "Since our last conversation, I've been thinking about your [specific challenge]",
                            "I have some additional ideas that might help",
                            "How has [situation they mentioned] been going?"
                        ]
                    }
                ]
            }
        }
        
        # Persuasive insights database (Cluely.ai style)
        self.persuasive_insights = {
            "urgency_builders": [
                "Companies that implement this see results within the first 30 days",
                "Your competitors are already using solutions like this",
                "The cost of waiting is often higher than the cost of acting"
            ],
            "social_proof": [
                "Over 500 companies in your industry trust us with this",
                "Our clients typically see a 40% improvement in [relevant metric]",
                "[Similar company name] saw [specific result] after implementing this"
            ],
            "risk_reversal": [
                "We offer a 30-day money-back guarantee",
                "You can start with a pilot program to test the results",
                "There's no long-term commitment required"
            ],
            "scarcity": [
                "We only onboard 5 new clients per month to ensure quality",
                "This pricing is only available until [date]",
                "We have limited spots for our Q1 implementation cohort"
            ]
        }
    
    async def initialize(self, conversation_type: str = "sales_discovery"):
        """Initialize teleprompter for specific conversation type"""
        try:
            self.current_talk_track = self.talk_tracks.get(conversation_type, self.talk_tracks["sales_discovery"])
            self.conversation_stage = self.current_talk_track["stages"][0]["name"]
            self.is_active = True
            
            # Load initial prompts
            await self._load_stage_prompts()
            
            logger.info(f"Adaptive Teleprompter initialized for {conversation_type}")
            
        except Exception as e:
            logger.error(f"Error initializing teleprompter: {e}")
            raise
    
    async def process_conversation_update(
        self,
        text: str,
        speaker: str,
        conversation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process conversation update and adapt prompts - Core Cluely.ai functionality"""
        try:
            if not self.is_active:
                return {"prompts": [], "stage": self.conversation_stage}
            
            # Analyze conversation for stage progression
            stage_changed = await self._analyze_stage_progression(text, speaker)
            
            # Generate adaptive prompts based on context
            adaptive_prompts = await self._generate_adaptive_prompts(text, speaker, conversation_context)
            
            # Add persuasive insights if appropriate
            persuasive_prompts = await self._generate_persuasive_insights(conversation_context)
            
            # Combine all prompts
            all_prompts = []
            all_prompts.extend(adaptive_prompts)
            all_prompts.extend(persuasive_prompts)
            
            # Store in history
            self.prompt_history.append({
                "timestamp": datetime.utcnow(),
                "stage": self.conversation_stage,
                "prompts": all_prompts,
                "trigger_text": text[:100]
            })
            
            return {
                "prompts": all_prompts,
                "stage": self.conversation_stage,
                "stage_changed": stage_changed,
                "talk_track_progress": self._get_talk_track_progress()
            }
            
        except Exception as e:
            logger.error(f"Error processing conversation update: {e}")
            return {"prompts": [], "stage": self.conversation_stage}
    
    async def _analyze_stage_progression(self, text: str, speaker: str) -> bool:
        """Analyze if conversation should progress to next stage"""
        try:
            if speaker == "user":  # Don't progress on user speech
                return False
            
            current_stage_info = self._get_current_stage_info()
            if not current_stage_info:
                return False
            
            # Check for stage progression triggers
            triggers = current_stage_info.get("next_stage_triggers", [])
            text_lower = text.lower()
            
            for trigger in triggers:
                if trigger.lower() in text_lower:
                    # Progress to next stage
                    await self._progress_to_next_stage()
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error analyzing stage progression: {e}")
            return False
    
    async def _progress_to_next_stage(self):
        """Progress to the next conversation stage"""
        try:
            current_stages = self.current_talk_track["stages"]
            current_index = next(
                (i for i, stage in enumerate(current_stages) if stage["name"] == self.conversation_stage),
                -1
            )
            
            if current_index >= 0 and current_index < len(current_stages) - 1:
                self.conversation_stage = current_stages[current_index + 1]["name"]
                await self._load_stage_prompts()
                logger.info(f"Progressed to stage: {self.conversation_stage}")
            
        except Exception as e:
            logger.error(f"Error progressing to next stage: {e}")
    
    async def _load_stage_prompts(self):
        """Load prompts for current stage"""
        try:
            stage_info = self._get_current_stage_info()
            if stage_info:
                self.active_prompts = stage_info.get("prompts", [])
            
        except Exception as e:
            logger.error(f"Error loading stage prompts: {e}")
    
    async def _generate_adaptive_prompts(
        self,
        text: str,
        speaker: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate adaptive prompts based on conversation context"""
        try:
            prompts = []
            
            # If prospect is speaking, generate response suggestions
            if speaker != "user":
                # Use AI to generate contextual prompts
                ai_prompt = f"""
                Based on this conversation context and the prospect's statement: "{text}"
                Generate 2-3 adaptive response prompts for a sales professional.
                Current conversation stage: {self.conversation_stage}
                
                Make the prompts:
                1. Contextually relevant to what was just said
                2. Appropriate for the current conversation stage
                3. Focused on moving the conversation forward
                4. Natural and conversational
                
                Format as brief, actionable prompts.
                """
                
                try:
                    response = await self.ai_engine.openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an expert sales coach providing real-time guidance."},
                            {"role": "user", "content": ai_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=300
                    )
                    
                    ai_suggestions = response.choices[0].message.content.strip().split('\n')
                    for suggestion in ai_suggestions:
                        if suggestion.strip():
                            prompts.append({
                                "type": "adaptive_response",
                                "text": suggestion.strip().lstrip('123456789.-• '),
                                "confidence": 0.8,
                                "stage": self.conversation_stage
                            })
                            
                except Exception as e:
                    logger.error(f"Error generating AI prompts: {e}")
            
            # Add stage-specific prompts
            stage_prompts = self.active_prompts[:2]  # Limit to 2 stage prompts
            for prompt_text in stage_prompts:
                prompts.append({
                    "type": "stage_prompt",
                    "text": prompt_text,
                    "confidence": 0.9,
                    "stage": self.conversation_stage
                })
            
            return prompts
            
        except Exception as e:
            logger.error(f"Error generating adaptive prompts: {e}")
            return []
    
    async def _generate_persuasive_insights(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate persuasive insights based on conversation context"""
        try:
            insights = []
            
            # Analyze context for appropriate persuasive techniques
            conversation_length = context.get("duration_seconds", 0)
            objections_count = len(context.get("objections", []))
            sentiment = context.get("sentiment", {}).get("overall", "neutral")
            
            # Add urgency builders if conversation is progressing well
            if conversation_length > 300 and sentiment in ["positive", "neutral"]:  # 5+ minutes
                urgency_insight = self.persuasive_insights["urgency_builders"][0]
                insights.append({
                    "type": "urgency_builder",
                    "text": urgency_insight,
                    "confidence": 0.7,
                    "reasoning": "Conversation progressing well, appropriate time for urgency"
                })
            
            # Add social proof if objections detected
            if objections_count > 0:
                social_proof = self.persuasive_insights["social_proof"][0]
                insights.append({
                    "type": "social_proof",
                    "text": social_proof,
                    "confidence": 0.8,
                    "reasoning": "Objections detected, social proof can help"
                })
            
            # Add risk reversal in closing stage
            if self.conversation_stage == "closing":
                risk_reversal = self.persuasive_insights["risk_reversal"][0]
                insights.append({
                    "type": "risk_reversal",
                    "text": risk_reversal,
                    "confidence": 0.9,
                    "reasoning": "Closing stage, reduce perceived risk"
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating persuasive insights: {e}")
            return []
    
    def _get_current_stage_info(self) -> Optional[Dict[str, Any]]:
        """Get information about current conversation stage"""
        try:
            for stage in self.current_talk_track["stages"]:
                if stage["name"] == self.conversation_stage:
                    return stage
            return None
            
        except Exception as e:
            logger.error(f"Error getting current stage info: {e}")
            return None
    
    def _get_talk_track_progress(self) -> Dict[str, Any]:
        """Get talk track progress information"""
        try:
            stages = self.current_talk_track["stages"]
            current_index = next(
                (i for i, stage in enumerate(stages) if stage["name"] == self.conversation_stage),
                0
            )
            
            return {
                "current_stage": self.conversation_stage,
                "stage_index": current_index,
                "total_stages": len(stages),
                "progress_percentage": (current_index / len(stages)) * 100,
                "next_stage": stages[current_index + 1]["name"] if current_index < len(stages) - 1 else None
            }
            
        except Exception as e:
            logger.error(f"Error getting talk track progress: {e}")
            return {}
    
    async def get_win_rate_analytics(self) -> Dict[str, Any]:
        """Get win rate analytics based on conversation performance"""
        try:
            # Analyze prompt usage and effectiveness
            total_prompts = len(self.prompt_history)
            if total_prompts == 0:
                return {"win_rate_prediction": 0.5, "confidence": 0.0}
            
            # Calculate metrics
            stage_progression_score = (len(set(p["stage"] for p in self.prompt_history)) / 5.0)  # 5 total stages
            prompt_variety_score = len(set(p["prompts"][0]["type"] for p in self.prompt_history if p["prompts"])) / 4.0  # 4 prompt types
            
            # Simple win rate prediction algorithm
            win_rate_prediction = min(1.0, (stage_progression_score + prompt_variety_score) / 2.0)
            
            return {
                "win_rate_prediction": win_rate_prediction,
                "confidence": 0.8,
                "stage_progression_score": stage_progression_score,
                "prompt_variety_score": prompt_variety_score,
                "total_prompts_used": total_prompts,
                "current_stage": self.conversation_stage,
                "recommendation": self._get_win_rate_recommendation(win_rate_prediction)
            }
            
        except Exception as e:
            logger.error(f"Error calculating win rate analytics: {e}")
            return {"win_rate_prediction": 0.5, "confidence": 0.0}
    
    def _get_win_rate_recommendation(self, win_rate: float) -> str:
        """Get recommendation based on win rate prediction"""
        if win_rate > 0.8:
            return "Excellent conversation flow! Continue with current approach."
        elif win_rate > 0.6:
            return "Good progress. Consider addressing any remaining objections."
        elif win_rate > 0.4:
            return "Moderate progress. Focus on discovery and value demonstration."
        else:
            return "Consider pivoting approach. Ask more discovery questions."
    
    async def stop(self):
        """Stop the teleprompter"""
        self.is_active = False
        logger.info("Adaptive Teleprompter stopped")
