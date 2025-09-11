"""
Tests for the Audio Processor component.
"""
import pytest
import numpy as np
from typing import Dict, Any

from app.services.audio_processor import AudioProcessor

pytestmark = pytest.mark.audio

@pytest.mark.asyncio
async def test_audio_processor_initialization(audio_processor: AudioProcessor):
    """Test that the Audio Processor initializes correctly."""
    assert audio_processor.is_ready
    assert hasattr(audio_processor, 'vad')
    assert hasattr(audio_processor, 'whisper_model')

@pytest.mark.asyncio
async def test_voice_activity_detection(audio_processor: AudioProcessor):
    """Test voice activity detection."""
    # Create a sample audio frame (1 second of silence)
    sample_rate = 16000
    frame_duration = 1.0
    audio_frame = np.zeros(int(sample_rate * frame_duration), dtype=np.float32)

    # Test silence detection
    is_speech = await audio_processor.detect_voice_activity(audio_frame)
    assert isinstance(is_speech, bool)
    assert not is_speech  # Should be False for silence

    # Create a sample audio frame with speech-like content
    t = np.linspace(0, frame_duration, int(sample_rate * frame_duration))
    audio_frame = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz tone

    # Test speech detection
    is_speech = await audio_processor.detect_voice_activity(audio_frame)
    assert isinstance(is_speech, bool)
    assert is_speech  # Should be True for speech-like content

@pytest.mark.asyncio
async def test_transcribe_audio(audio_processor: AudioProcessor):
    """Test audio transcription."""
    # Create a sample audio file (1 second of silence)
    sample_rate = 16000
    duration = 1.0
    audio_data = np.zeros(int(sample_rate * duration), dtype=np.float32)

    # Test transcription
    result = await audio_processor.transcribe_audio(audio_data)
    assert isinstance(result, dict)
    assert "text" in result
    assert "language" in result
    assert "segments" in result

@pytest.mark.asyncio
async def test_diarization(audio_processor: AudioProcessor):
    """Test speaker diarization."""
    # Create a sample multi-speaker audio file
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create two different tones to simulate different speakers
    speaker1 = 0.5 * np.sin(2 * np.pi * 440 * t[:len(t)//2])  # 440 Hz
    speaker2 = 0.5 * np.sin(2 * np.pi * 880 * t[len(t)//2:])  # 880 Hz
    audio_data = np.concatenate([speaker1, speaker2])

    # Test diarization
    result = await audio_processor.diarize_speakers(audio_data)
    assert isinstance(result, list)
    assert len(result) > 0
    for segment in result:
        assert "start" in segment
        assert "end" in segment
        assert "speaker" in segment

@pytest.mark.asyncio
async def test_noise_reduction(audio_processor: AudioProcessor):
    """Test noise reduction."""
    # Create a noisy audio sample
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Signal + noise
    signal = 0.5 * np.sin(2 * np.pi * 440 * t)  # Clean signal
    noise = 0.1 * np.random.randn(len(t))  # Random noise
    noisy_audio = signal + noise

    # Test noise reduction
    cleaned_audio = await audio_processor.reduce_noise(noisy_audio)
    assert isinstance(cleaned_audio, np.ndarray)
    assert len(cleaned_audio) == len(noisy_audio)
    
    # Check that noise has been reduced
    noise_before = np.std(noisy_audio - signal)
    noise_after = np.std(cleaned_audio - signal)
    assert noise_after < noise_before

@pytest.mark.asyncio
async def test_error_handling(audio_processor: AudioProcessor):
    """Test error handling in Audio Processor."""
    with pytest.raises(ValueError):
        await audio_processor.detect_voice_activity(np.array([]))

    with pytest.raises(ValueError):
        await audio_processor.transcribe_audio(np.array([]))

    with pytest.raises(ValueError):
        await audio_processor.diarize_speakers(np.array([]))

    with pytest.raises(ValueError):
        await audio_processor.reduce_noise(np.array([]))
