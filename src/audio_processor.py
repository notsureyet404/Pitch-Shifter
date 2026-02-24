import librosa
import numpy as np
import soundfile as sf
import io
from pedalboard import Pedalboard, PitchShift

# Krumhansl-Schmuckler key-finding algorithm profiles
# Adjusted to sum to 1 or normalized if needed, but relative strength matters.
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

PITCH_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def detect_key(file_path):
    """
    Detects the musical key of an audio file.

    Args:
        file_path (str): Path to the audio file.

    Returns:
        str: Detected key (e.g., "C Major", "A# Minor").
    """
    try:
        y, sr = librosa.load(file_path)

        # Extract Chroma features (12 bins)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

        # Sum chroma features over time to get a single vector representing the whole track
        chroma_sum = np.sum(chroma, axis=1)

        # Normalize
        chroma_sum = chroma_sum / np.max(chroma_sum)

        max_corr = -1
        detected_key = ""

        # Correlate with all 12 major and 12 minor keys
        for i in range(12):
            # Rotate profile to match the root note
            major_profile_rotated = np.roll(MAJOR_PROFILE, i)
            minor_profile_rotated = np.roll(MINOR_PROFILE, i)

            # Calculate correlation
            corr_major = np.corrcoef(chroma_sum, major_profile_rotated)[0, 1]
            corr_minor = np.corrcoef(chroma_sum, minor_profile_rotated)[0, 1]

            if corr_major > max_corr:
                max_corr = corr_major
                detected_key = f"{PITCH_NAMES[i]} Major"

            if corr_minor > max_corr:
                max_corr = corr_minor
                detected_key = f"{PITCH_NAMES[i]} Minor"

        return detected_key

    except Exception as e:
        print(f"Error detecting key: {e}")
        return "Unknown"

def process_audio(file_path, semitones):
    """
    Shifts the pitch of the audio file by the given semitones.

    Args:
        file_path (str): Path to the audio file.
        semitones (float): Number of semitones to shift (can be float, usually int for equal temperament).

    Returns:
        io.BytesIO: Buffer containing the processed audio in WAV format.
    """
    try:
        # Read audio using soundfile to get data and sample rate
        with sf.SoundFile(file_path) as f:
            audio = f.read(dtype='float32')
            samplerate = f.samplerate

        # Pedalboard expects (channels, samples) if stereo, or (samples,) if mono?
        # Let's check pedalboard docs or assume standard numpy array handling.
        # Soundfile returns (samples, channels) by default.
        # Pedalboard usually works with (channels, samples).

        # Transpose if necessary
        if audio.ndim > 1:
            audio = audio.T

        # Create Pedalboard
        board = Pedalboard([PitchShift(semitones=semitones)])

        # Process audio
        # process method takes (input_audio, sample_rate)
        processed_audio = board(audio, samplerate)

        # Prepare output buffer
        output_buffer = io.BytesIO()

        # Write to buffer using soundfile
        # Soundfile write expects (samples, channels), so we might need to transpose back
        if processed_audio.ndim > 1:
            processed_audio = processed_audio.T

        sf.write(output_buffer, processed_audio, samplerate, format='WAV')
        output_buffer.seek(0)

        return output_buffer

    except Exception as e:
        print(f"Error processing audio: {e}")
        return None

def get_target_key(original_key, semitones):
    """
    Calculates the target key based on the original key and semitone shift.

    Args:
        original_key (str): The original key (e.g., "C Major").
        semitones (int): The shift in semitones.

    Returns:
        str: The target key.
    """
    if not original_key or original_key == "Unknown":
        return "Unknown"

    try:
        parts = original_key.split(' ')
        root = parts[0]
        mode = ' '.join(parts[1:])

        if root not in PITCH_NAMES:
            return original_key # Should not happen if detected correctly

        root_idx = PITCH_NAMES.index(root)
        new_root_idx = (root_idx + int(semitones)) % 12
        new_root = PITCH_NAMES[new_root_idx]

        return f"{new_root} {mode}"

    except Exception as e:
        print(f"Error calculating target key: {e}")
        return original_key
