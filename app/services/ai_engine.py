"""
Core AI Engine for conversation analysis, objection detection, and response generation
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import openai
from anthropic import Anthropic
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from loguru import logger
import re

from app.core.config import settings
from app.models.conversation import Conversation, ObjectionEvent
from app.services.vector_store import VectorStore
from app.services.teleprompter import AdaptiveTeleprompter
from app.services.win_rate_analyzer import WinRateAnalyzer
from app.services.platform_integrations import PlatformIntegrationManager


class AIEngine:
    """Main AI engine for conversation processing"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.embedding_model = None
        self.sentiment_analyzer = None
        self.objection_classifier = None
        self.vector_store = None
        
        # Cluely.ai core features
        self.teleprompter = None
        self.win_rate_analyzer = None
        self.platform_manager = None
        
        self.is_ready = False
        
        # Objection patterns and responses
        self.objection_patterns = {
            "price": {
                "patterns": [
                    r"too expensive", r"cost too much", r"price is high", r"can't afford",
                    r"budget", r"cheaper alternative", r"too pricey", r"over budget"
                ],
                "category": "pricing",
                "urgency": "high"
            },
            "timing": {
                "patterns": [
                    r"not the right time", r"maybe later", r"next quarter", r"too busy",
                    r"need more time", r"timing isn't right", r"call back later"
                ],
                "category": "timing",
                "urgency": "medium"
            },
            "authority": {
                "patterns": [
                    r"need to check with", r"not my decision", r"have to ask",
                    r"need approval", r"boss decides", r"team decision"
                ],
                "category": "authority",
                "urgency": "high"
            },
            "competition": {
                "patterns": [
                    r"already using", r"competitor", r"other solution", r"different vendor",
                    r"current provider", r"existing system", r"another option"
                ],
                "category": "competition",
                "urgency": "high"
            },
            "trust": {
                "patterns": [
                    r"never heard of", r"not sure about", r"don't trust", r"seems risky",
                    r"not confident", r"unknown company", r"need references"
                ],
                "category": "trust",
                "urgency": "high"
            },
            "features": {
                "patterns": [
                    r"doesn't have", r"missing feature", r"need more", r"not enough",
                    r"lacks", r"insufficient", r"limited functionality"
                ],
                "category": "features",
                "urgency": "medium"
            }
        }
        
        # Response templates
        self.response_templates = {
            "price": [
                "I understand budget is important. Let me show you the ROI calculation...",
                "What if we could structure this to fit your budget? Let's explore options...",
                "The cost of not solving this problem is often much higher. Consider..."
            ],
            "timing": [
                "I appreciate you being upfront about timing. What would need to change for this to become a priority?",
                "What's driving the current timeline? Perhaps we can find a way to start small...",
                "Many clients initially felt the same way. What changed their minds was..."
            ],
            "authority": [
                "I completely understand. Who else would be involved in this decision?",
                "That makes sense. What information would help you present this to your team?",
                "What criteria will they use to evaluate this? Let me help you build the case..."
            ],
            "competition": [
                "That's great that you're being thorough. What's working well with your current solution?",
                "What gaps exist in your current setup that we might be able to address?",
                "How are you measuring success with your current provider?"
            ],
            "trust": [
                "I completely understand wanting to work with a trusted partner. Let me share some references...",
                "What would help build your confidence in our solution?",
                "Many of our clients initially felt the same way. Here's what changed their minds..."
            ],
            "features": [
                "That's a great point. Let me show you how we handle that specific use case...",
                "What specific functionality are you looking for? We might have that...",
                "Our clients often discover features they didn't know they needed. For example..."
            ]
        }
    
    async def initialize(self):
        """Initialize all AI models and services"""
        try:
            logger.info("Initializing AI Engine...")
            
            # Initialize OpenAI
            self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Initialize Anthropic if available
            if settings.ANTHROPIC_API_KEY:
                self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                
            # Initialize Cohere if available
            if settings.COHERE_API_KEY:
                import cohere
                self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
            
            # Initialize embedding model
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize sentiment analyzer
            logger.info("Loading sentiment analyzer...")
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # Initialize objection classifier
            logger.info("Loading objection classifier...")
            self.objection_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium"
            )
            
            # Initialize vector store
            self.vector_store = VectorStore()
            await self.vector_store.initialize()
            
            # Initialize Cluely.ai core features
            self.teleprompter = AdaptiveTeleprompter(self)
            self.win_rate_analyzer = WinRateAnalyzer(self)
            self.platform_manager = PlatformIntegrationManager()
            await self.platform_manager.initialize()
            
            self.is_ready = True
            logger.success("AI Engine with Cluely.ai features initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Engine: {e}")
            raise
    
    async def get_cohere_embeddings(
        self,
        texts: List[str],
        model: str = "embed-english-v3.0",
        input_type: str = "search_document",
        truncate: str = "END"
    ) -> List[List[float]]:
        """Get embeddings using Cohere's API"""
        if not hasattr(self, 'cohere_client'):
            raise ValueError("Cohere client not initialized. Please set COHERE_API_KEY in environment variables.")
            
        try:
            response = self.cohere_client.embed(
                texts=texts,
                model=model,
                input_type=input_type,
                truncate=truncate
            )
            
            return response.embeddings
            
        except Exception as e:
            logger.error(f"Error getting embeddings with Cohere: {e}")
            raise
            
    async def generate_with_cohere(
        self,
        prompt: str,
        model: str = "command",
        max_tokens: int = 500,
        temperature: float = 0.7,
        k: int = 0,
        p: float = 0.75,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
        stop_sequences: Optional[List[str]] = None,
        return_likelihoods: str = "NONE",
        truncate: str = "END",
        num_generations: int = 1,
    ) -> List[str]:
        """Generate text using Cohere's API"""
        if not hasattr(self, 'cohere_client'):
            raise ValueError("Cohere client not initialized. Please set COHERE_API_KEY in environment variables.")
            
        try:
            response = self.cohere_client.generate(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                k=k,
                p=p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop_sequences=stop_sequences,
                return_likelihoods=return_likelihoods,
                truncate=truncate,
                num_generations=num_generations,
            )
            
            return [generation.text for generation in response.generations]
            
        except Exception as e:
            logger.error(f"Error generating text with Cohere: {e}")
            raise
            
    async def analyze_conversation_chunk(
        self,
        text: str,
        speaker: str,
        timestamp: datetime,
        conversation_id: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Analyze a chunk of conversation in real-time"""
        try:
            # Parallel analysis
            tasks = [
                self._analyze_sentiment(text),
                self._detect_objections(text, speaker),
                self._analyze_engagement(text, speaker),
                self._extract_entities(text),
                self._generate_suggestions(text, speaker, context or {})
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            sentiment = results[0] if not isinstance(results[0], Exception) else {}
            objections = results[1] if not isinstance(results[1], Exception) else []
            engagement = results[2] if not isinstance(results[2], Exception) else {}
            entities = results[3] if not isinstance(results[3], Exception) else {}
            suggestions = results[4] if not isinstance(results[4], Exception) else []
            
            analysis = {
                "conversation_id": conversation_id,
                "timestamp": timestamp.isoformat(),
                "speaker": speaker,
                "text": text,
                "sentiment": sentiment,
                "objections": objections,
                "engagement": engagement,
                "entities": entities,
                "suggestions": suggestions,
                "processed_at": datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing conversation chunk: {e}")
            return {"error": str(e)}
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            # Use the sentiment analyzer
            results = self.sentiment_analyzer(text)
            
            # Convert to our format
            sentiment_scores = {}
            for result in results[0]:  # First result contains all scores
                label = result['label'].lower()
                score = result['score']
                sentiment_scores[label] = score
            
            # Determine overall sentiment
            max_sentiment = max(sentiment_scores.items(), key=lambda x: x[1])
            
            return {
                "overall": max_sentiment[0],
                "confidence": max_sentiment[1],
                "scores": sentiment_scores,
                "valence": self._calculate_valence(sentiment_scores)
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {"error": str(e)}
    
    async def _detect_objections(self, text: str, speaker: str) -> List[Dict[str, Any]]:
        """Detect objections in conversation"""
        try:
            objections = []
            text_lower = text.lower()
            
            for objection_type, config in self.objection_patterns.items():
                for pattern in config["patterns"]:
                    if re.search(pattern, text_lower):
                        objection = {
                            "type": objection_type,
                            "category": config["category"],
                            "urgency": config["urgency"],
                            "pattern_matched": pattern,
                            "speaker": speaker,
                            "confidence": self._calculate_objection_confidence(text, pattern),
                            "suggested_responses": self.response_templates.get(objection_type, [])
                        }
                        objections.append(objection)
            
            return objections
            
        except Exception as e:
            logger.error(f"Error detecting objections: {e}")
            return []
    
    async def _analyze_engagement(self, text: str, speaker: str) -> Dict[str, Any]:
        """Analyze engagement level from text"""
        try:
            # Simple engagement metrics
            word_count = len(text.split())
            question_count = text.count('?')
            exclamation_count = text.count('!')
            
            # Calculate engagement score
            engagement_score = min(1.0, (word_count / 50) + (question_count * 0.1) + (exclamation_count * 0.05))
            
            return {
                "score": engagement_score,
                "word_count": word_count,
                "questions": question_count,
                "exclamations": exclamation_count,
                "speaker": speaker
            }
            
        except Exception as e:
            logger.error(f"Error analyzing engagement: {e}")
            return {}
    
    async def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text using OpenAI"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract key entities (companies, products, people, dates, numbers) from the following text. Return as JSON."},
                    {"role": "user", "content": text}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            entities_text = response.choices[0].message.content
            try:
                entities = json.loads(entities_text)
                return entities
            except json.JSONDecodeError:
                return {"raw_entities": entities_text}
                
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {}
    
    async def _generate_suggestions(
        self,
        text: str,
        speaker: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate real-time suggestions"""
        try:
            suggestions = []
            
            # If it's a prospect/customer speaking, generate responses
            if speaker != "user":
                # Get relevant documents
                relevant_docs = await self.vector_store.search_similar(text, limit=3)
                
                # Generate contextual response
                response = await self.openai_client.chat.completions.create(
                    model=settings.DEFAULT_AI_MODEL,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt(context)},
                        {"role": "user", "content": f"Prospect said: '{text}'. Suggest 2-3 helpful responses."}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                
                suggestions_text = response.choices[0].message.content
                
                # Parse suggestions
                suggestion_lines = suggestions_text.split('\n')
                for line in suggestion_lines:
                    if line.strip() and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                        suggestions.append({
                            "type": "response",
                            "text": line.strip().lstrip('-•123456789. '),
                            "confidence": 0.8,
                            "relevant_docs": [doc["id"] for doc in relevant_docs]
                        })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Generate system prompt based on context"""
        base_prompt = """You are an AI sales assistant providing real-time coaching. 
        Generate helpful, natural responses that move the conversation forward positively.
        Focus on building rapport, addressing concerns, and advancing the sales process."""
        
        if context.get("conversation_type") == "demo":
            base_prompt += " This is a product demonstration. Focus on features and benefits."
        elif context.get("conversation_type") == "discovery":
            base_prompt += " This is a discovery call. Focus on asking good questions and understanding needs."
        elif context.get("conversation_type") == "closing":
            base_prompt += " This is a closing conversation. Focus on overcoming final objections and securing commitment."
        
        return base_prompt
    
    def _calculate_valence(self, sentiment_scores: Dict[str, float]) -> float:
        """Calculate emotional valence (-1 to 1)"""
        positive = sentiment_scores.get('positive', 0)
        negative = sentiment_scores.get('negative', 0)
        return positive - negative
    
    def _calculate_objection_confidence(self, text: str, pattern: str) -> float:
        """Calculate confidence score for objection detection"""
        # Simple confidence based on pattern match strength
        matches = len(re.findall(pattern, text.lower()))
        return min(1.0, matches * 0.3 + 0.4)
    
    async def generate_follow_up_email(
        self,
        conversation_summary: str,
        participant_info: Dict[str, Any],
        key_points: List[str]
    ) -> str:
        """Generate personalized follow-up email"""
        try:
            prompt = f"""
            Generate a professional follow-up email based on this conversation:
            
            Conversation Summary: {conversation_summary}
            Participant: {participant_info.get('name', 'N/A')} at {participant_info.get('company', 'N/A')}
            Key Points Discussed: {', '.join(key_points)}
            
            Make it personal, reference specific points discussed, and include clear next steps.
            """
            
            response = await self.openai_client.chat.completions.create(
                model=settings.DEFAULT_AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional sales assistant writing follow-up emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating follow-up email: {e}")
            return ""
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.vector_store:
            await self.vector_store.cleanup()
        self.is_ready = False
        logger.info("AI Engine cleaned up")
