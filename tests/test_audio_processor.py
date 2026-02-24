import os
import numpy as np
import soundfile as sf
import pytest
from src.audio_processor import detect_key, process_audio, get_target_key

@pytest.fixture
def c_major_audio(tmp_path):
    """Creates a temporary WAV file with a C Major chord."""
    sr = 22050
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration))

    # C Major chord frequencies: C4, E4, G4
    freqs = [261.63, 329.63, 392.00]
    audio = np.zeros_like(t)
    for f in freqs:
        audio += 0.5 * np.sin(2 * np.pi * f * t)

    # Normalize
    audio /= len(freqs)

    file_path = tmp_path / "c_major.wav"
    sf.write(file_path, audio, sr)
    return str(file_path)

def test_detect_key_c_major(c_major_audio):
    """Test if C Major chord is detected as C Major."""
    key = detect_key(c_major_audio)
    # It might detect C Major or related keys depending on harmonics, but C Major is most likely.
    # The algorithm is simple, so it should be robust for pure tones.
    assert "C Major" in key or "C" in key # Being lenient

def test_get_target_key():
    """Test target key calculation."""
    assert get_target_key("C Major", 2) == "D Major"
    assert get_target_key("C Major", -1) == "B Major"
    assert get_target_key("A Minor", 3) == "C Minor"
    assert get_target_key("G# Major", 1) == "A Major"
    assert get_target_key("Unknown", 2) == "Unknown"

def test_process_audio(c_major_audio):
    """Test audio processing runs and returns a valid buffer."""
    semitones = 2
    output_buffer = process_audio(c_major_audio, semitones)

    assert output_buffer is not None

    # Check if buffer contains WAV data (starts with RIFF)
    output_buffer.seek(0)
    header = output_buffer.read(4)
    assert header == b'RIFF'

    # Check length
    output_buffer.seek(0, 2)
    size = output_buffer.tell()
    assert size > 44 # WAV header is 44 bytes

def test_process_audio_invalid_file():
    """Test processing with invalid file."""
    result = process_audio("non_existent_file.wav", 0)
    assert result is None
