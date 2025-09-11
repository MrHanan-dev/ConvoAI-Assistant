"""
Tests for the AI Engine component.
"""
import pytest
from datetime import datetime
from typing import Dict, Any

from app.services.ai_engine import AIEngine

pytestmark = pytest.mark.ai

@pytest.mark.asyncio
async def test_ai_engine_initialization(ai_engine: AIEngine):
    """Test that the AI Engine initializes correctly."""
    assert ai_engine.is_ready
    assert hasattr(ai_engine, 'cohere_client')
    assert hasattr(ai_engine, 'openai_client')
    assert hasattr(ai_engine, 'vector_store')

@pytest.mark.asyncio
async def test_generate_with_cohere(ai_engine: AIEngine):
    """Test text generation using Cohere."""
    prompt = "What are the best practices for sales calls?"
    responses = await ai_engine.generate_with_cohere(prompt)
    assert isinstance(responses, list)
    assert len(responses) > 0
    assert isinstance(responses[0], str)

@pytest.mark.asyncio
async def test_get_cohere_embeddings(ai_engine: AIEngine):
    """Test getting embeddings using Cohere."""
    texts = ["How can I help you?", "What's your budget?"]
    embeddings = await ai_engine.get_cohere_embeddings(texts)
    assert isinstance(embeddings, list)
    assert len(embeddings) == 2
    assert isinstance(embeddings[0], list)
    assert len(embeddings[0]) > 0
    assert all(isinstance(x, float) for x in embeddings[0])

@pytest.mark.asyncio
async def test_analyze_conversation_chunk(ai_engine: AIEngine):
    """Test conversation chunk analysis."""
    text = "I'm interested in your enterprise plan."
    speaker = "customer"
    timestamp = datetime.utcnow()
    conversation_id = "test-conversation"
    context = {"meeting_type": "sales"}

    result = await ai_engine.analyze_conversation_chunk(
        text=text,
        speaker=speaker,
        timestamp=timestamp,
        conversation_id=conversation_id,
        context=context
    )

    assert isinstance(result, dict)
    assert "sentiment" in result
    assert "intent" in result
    assert "topics" in result
    assert "next_steps" in result

@pytest.mark.asyncio
async def test_handle_objection(ai_engine: AIEngine):
    """Test objection handling."""
    objection = "Your product is too expensive."
    context = {
        "product": "Enterprise Plan",
        "price": "$1000/month",
        "features": ["AI Assistant", "Team Management", "Analytics"]
    }

    response = await ai_engine.handle_objection(objection, context)
    assert isinstance(response, dict)
    assert "response" in response
    assert "confidence" in response
    assert "suggested_approach" in response

@pytest.mark.asyncio
async def test_generate_insights(ai_engine: AIEngine):
    """Test insight generation."""
    conversation_text = """
    Customer: I'm looking for a solution to help our sales team.
    Agent: I understand. Can you tell me more about your team size and current challenges?
    Customer: We have about 50 sales reps, and we're struggling with call quality.
    """
    result = await ai_engine.generate_insights(conversation_text)
    assert isinstance(result, dict)
    assert "key_points" in result
    assert "action_items" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_error_handling(ai_engine: AIEngine):
    """Test error handling in AI Engine."""
    with pytest.raises(ValueError):
        await ai_engine.generate_with_cohere("")

    with pytest.raises(ValueError):
        await ai_engine.get_cohere_embeddings([])

    with pytest.raises(ValueError):
        await ai_engine.analyze_conversation_chunk(
            text="",
            speaker="",
            timestamp=datetime.utcnow(),
            conversation_id="",
            context={}
        )
