# Pitch-Shifter

A professional Python desktop application for high-fidelity audio pitch shifting, featuring automatic key detection and real-time musical key mapping.

---

## 1. Overview
This application provides a seamless "Vibe Coding" inspired workflow for musicians and audio engineers. By leveraging advanced DSP libraries and a modern GUI framework, it automates the tedious process of manual key detection and pitch calculation.

## 2. Technical Stack
- **GUI Framework**: `Flet` (Flutter-based for Python)
- **Audio Analysis**: `librosa` (Chroma feature extraction)
- **DSP Engine**: `pedalboard` (Spotify's high-quality PitchShift processor)
- **Audio I/O**: `soundfile`, `io.BytesIO`

## 3. Functional Requirements

### A. User Interface (UI)
- **Theme**: Dark mode by default for a professional DAW (Digital Audio Workstation) aesthetic.
- **Layout**:
  - **Top**: File uploader supporting `MP3`, `WAV`, and `FLAC`.
  - **Middle**: Large, prominent display panel for detected/target musical key (e.g., "Ab Major").
  - **Bottom**: Horizontal slider for Pitch adjustment (Range: -12 to +12, Step: 1).
  - **Action**: "Apply" button and an integrated audio player for previewing results.

### B. Core Logic
- **Key Detection**: Upon file upload, analyze the audio to detect the root note and scale.
- **Real-time Mapping**: As the user moves the slider, the UI instantly updates the displayed "Target Key" using the 12-tone equal temperament scale.
- **High-Fidelity Processing**: Execute pitch shifting via `pedalboard.PitchShift`. All processing is handled in-memory using `BytesIO` to ensure speed and zero disk clutter.

### C. Output
- **Preview**: Integrated on-screen audio player for immediate feedback.
- **Export**: Functional "Save" capability to export the processed audio to the local file system.

## 4. Development Requirements
- **Entry Point**: `main.py`
- **Python Version**: 3.9+
- **System Dependencies**:
  - `FFmpeg` (Required for audio decoding)
  - `libsndfile` (Required for `librosa` and `soundfile`)
- **Python Dependencies**: Defined in `requirements.txt`

## 5. Definition of Done
- [ ] Successful automatic detection of musical key after file upload.
- [ ] UI correctly updates target key labels in real-time during slider interaction.
- [ ] High-quality audio output without significant artifacts or latency.
- [ ] Functional save/export capability to local storage.
