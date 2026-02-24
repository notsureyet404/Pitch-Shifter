FROM python:3.12-slim

# Install system dependencies
# ffmpeg: for audio processing
# libsndfile1: for soundfile/librosa
# libgomp1: often required by numpy/scipy/scikit-learn
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
# PYTHONUNBUFFERED=1 ensures logs are visible immediately
ENV PYTHONUNBUFFERED=1

# Run the Flet application
# Render provides the PORT environment variable.
# We use shell form to expand the variable.
# --web: Run in web mode
# --port: Bind to the specified port
# --host 0.0.0.0: Bind to all interfaces (required for Docker/Render)
CMD ["sh", "-c", "flet run --web --port ${PORT:-8000} --host 0.0.0.0 main.py"]
