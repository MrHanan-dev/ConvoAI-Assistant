"""
Tests for the Conversation Analyzer component.
"""
import pytest
from datetime import datetime
from typing import Dict, Any

from app.services.conversation_analyzer import ConversationAnalyzer

pytestmark = pytest.mark.integration

@pytest.mark.asyncio
async def test_conversation_analyzer_initialization(conversation_analyzer: ConversationAnalyzer):
    """Test that the Conversation Analyzer initializes correctly."""
    assert conversation_analyzer.is_ready
    assert hasattr(conversation_analyzer, 'ai_engine')
    assert hasattr(conversation_analyzer, 'audio_processor')

@pytest.mark.asyncio
async def test_analyze_live_conversation(conversation_analyzer: ConversationAnalyzer):
    """Test live conversation analysis."""
    conversation_id = "test-live-conversation"
    speaker = "agent"
    text = "Hi, I'm John from sales. How can I help you today?"
    timestamp = datetime.utcnow()

    result = await conversation_analyzer.analyze_live_conversation(
        conversation_id=conversation_id,
        speaker=speaker,
        text=text,
        timestamp=timestamp
    )

    assert isinstance(result, dict)
    assert "real_time_insights" in result
    assert "suggested_responses" in result
    assert "alerts" in result
    assert "sentiment_score" in result

@pytest.mark.asyncio
async def test_analyze_recorded_conversation(conversation_analyzer: ConversationAnalyzer):
    """Test recorded conversation analysis."""
    conversation = {
        "id": "test-recorded-conversation",
        "participants": ["agent", "customer"],
        "transcript": [
            {
                "speaker": "agent",
                "text": "Hi, I'm John from sales. How can I help you today?",
                "timestamp": datetime.utcnow()
            },
            {
                "speaker": "customer",
                "text": "I'm interested in your enterprise solution.",
                "timestamp": datetime.utcnow()
            }
        ]
    }

    result = await conversation_analyzer.analyze_recorded_conversation(conversation)
    assert isinstance(result, dict)
    assert "summary" in result
    assert "key_points" in result
    assert "action_items" in result
    assert "sentiment_analysis" in result
    assert "conversation_quality_score" in result

@pytest.mark.asyncio
async def test_generate_coaching_insights(conversation_analyzer: ConversationAnalyzer):
    """Test coaching insights generation."""
    conversation_id = "test-coaching-conversation"
    agent_id = "test-agent"

    result = await conversation_analyzer.generate_coaching_insights(
        conversation_id=conversation_id,
        agent_id=agent_id
    )

    assert isinstance(result, dict)
    assert "strengths" in result
    assert "areas_for_improvement" in result
    assert "recommended_actions" in result
    assert "best_practices_comparison" in result

@pytest.mark.asyncio
async def test_detect_objections(conversation_analyzer: ConversationAnalyzer):
    """Test objection detection."""
    text = "That's a bit expensive for our budget right now."
    context = {
        "product": "Enterprise Plan",
        "price_point": "high",
        "previous_objections": []
    }

    result = await conversation_analyzer.detect_objections(text, context)
    assert isinstance(result, dict)
    assert "is_objection" in result
    assert "objection_type" in result
    assert "confidence_score" in result
    assert "recommended_response" in result

@pytest.mark.asyncio
async def test_analyze_call_quality(conversation_analyzer: ConversationAnalyzer):
    """Test call quality analysis."""
    conversation_metrics = {
        "duration": 300,  # 5 minutes
        "speaker_ratio": {"agent": 0.4, "customer": 0.6},
        "interruptions": 2,
        "silence_periods": 3,
        "talk_speed": 150  # words per minute
    }

    result = await conversation_analyzer.analyze_call_quality(conversation_metrics)
    assert isinstance(result, dict)
    assert "quality_score" in result
    assert "areas_of_concern" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_error_handling(conversation_analyzer: ConversationAnalyzer):
    """Test error handling in Conversation Analyzer."""
    with pytest.raises(ValueError):
        await conversation_analyzer.analyze_live_conversation(
            conversation_id="",
            speaker="",
            text="",
            timestamp=datetime.utcnow()
        )

    with pytest.raises(ValueError):
        await conversation_analyzer.analyze_recorded_conversation({})

    with pytest.raises(ValueError):
        await conversation_analyzer.generate_coaching_insights(
            conversation_id="",
            agent_id=""
        )
