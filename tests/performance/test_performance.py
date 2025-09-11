"""
Performance tests for the application.
"""
import pytest
import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any

from app.services.ai_engine import AIEngine
from app.services.audio_processor import AudioProcessor
from app.services.conversation_analyzer import ConversationAnalyzer

pytestmark = [pytest.mark.performance, pytest.mark.benchmark]

@pytest.mark.asyncio
async def test_ai_engine_performance(ai_engine: AIEngine, benchmark):
    """Test AI Engine performance."""
    # Prepare test data
    prompt = "What are the best practices for sales calls?"
    
    # Benchmark text generation
    def run_generation():
        return asyncio.run(ai_engine.generate_with_cohere(prompt))
    
    result = benchmark(run_generation)
    assert result is not None
    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_audio_processor_performance(audio_processor: AudioProcessor, benchmark):
    """Test Audio Processor performance."""
    # Prepare test data
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
    
    # Benchmark voice activity detection
    def run_vad():
        return asyncio.run(audio_processor.detect_voice_activity(audio_data))
    
    result = benchmark(run_vad)
    assert isinstance(result, bool)

@pytest.mark.asyncio
async def test_conversation_analyzer_performance(conversation_analyzer: ConversationAnalyzer, benchmark):
    """Test Conversation Analyzer performance."""
    # Prepare test data
    conversation_id = "test-performance"
    speaker = "agent"
    text = "Hi, I'm John from sales. How can I help you today?"
    timestamp = datetime.utcnow()
    
    # Benchmark live conversation analysis
    def run_analysis():
        return asyncio.run(conversation_analyzer.analyze_live_conversation(
            conversation_id=conversation_id,
            speaker=speaker,
            text=text,
            timestamp=timestamp
        ))
    
    result = benchmark(run_analysis)
    assert isinstance(result, dict)

@pytest.mark.asyncio
async def test_concurrent_processing(
    ai_engine: AIEngine,
    audio_processor: AudioProcessor,
    conversation_analyzer: ConversationAnalyzer,
    benchmark
):
    """Test concurrent processing performance."""
    # Prepare test data
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)
    
    conversation_id = "test-concurrent"
    speaker = "agent"
    text = "Hi, I'm John from sales. How can I help you today?"
    timestamp = datetime.utcnow()
    
    # Benchmark concurrent processing
    async def run_concurrent():
        tasks = [
            ai_engine.generate_with_cohere("What are the best practices for sales calls?"),
            audio_processor.detect_voice_activity(audio_data),
            conversation_analyzer.analyze_live_conversation(
                conversation_id=conversation_id,
                speaker=speaker,
                text=text,
                timestamp=timestamp
            )
        ]
        return await asyncio.gather(*tasks)
    
    def run_benchmark():
        return asyncio.run(run_concurrent())
    
    results = benchmark(run_benchmark)
    assert len(results) == 3
    assert all(result is not None for result in results)

@pytest.mark.asyncio
async def test_load_testing(
    ai_engine: AIEngine,
    audio_processor: AudioProcessor,
    conversation_analyzer: ConversationAnalyzer,
    benchmark
):
    """Test system performance under load."""
    # Prepare test data
    num_requests = 100
    requests = []
    
    for i in range(num_requests):
        timestamp = datetime.utcnow() + timedelta(seconds=i)
        requests.append({
            "conversation_id": f"test-load-{i}",
            "speaker": "agent" if i % 2 == 0 else "customer",
            "text": f"Test message {i}",
            "timestamp": timestamp
        })
    
    # Benchmark load testing
    async def process_request(request):
        return await conversation_analyzer.analyze_live_conversation(
            conversation_id=request["conversation_id"],
            speaker=request["speaker"],
            text=request["text"],
            timestamp=request["timestamp"]
        )
    
    async def run_load_test():
        tasks = [process_request(request) for request in requests]
        return await asyncio.gather(*tasks)
    
    def run_benchmark():
        return asyncio.run(run_load_test())
    
    results = benchmark(run_benchmark)
    assert len(results) == num_requests
    assert all(isinstance(result, dict) for result in results)

@pytest.mark.asyncio
async def test_memory_usage(
    ai_engine: AIEngine,
    audio_processor: AudioProcessor,
    conversation_analyzer: ConversationAnalyzer,
    benchmark
):
    """Test memory usage under continuous operation."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Run a series of operations
    async def run_operations():
        for i in range(100):
            await ai_engine.generate_with_cohere(f"Test prompt {i}")
            
            sample_rate = 16000
            duration = 1.0
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)
            await audio_processor.detect_voice_activity(audio_data)
            
            await conversation_analyzer.analyze_live_conversation(
                conversation_id=f"test-memory-{i}",
                speaker="agent",
                text=f"Test message {i}",
                timestamp=datetime.utcnow()
            )
    
    def run_benchmark():
        return asyncio.run(run_operations())
    
    benchmark(run_benchmark)
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Assert that memory increase is within acceptable limits (e.g., less than 100MB)
    assert memory_increase < 100 * 1024 * 1024  # 100MB in bytes
