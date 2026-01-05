FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    libsdl2-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libfreetype6-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# FIRST: Create a fresh requirements.txt with correct content
RUN echo "streamlit>=1.28.0" > requirements.txt && \
    echo "edge-tts>=6.1.9" >> requirements.txt && \
    echo "pygame>=2.5.0" >> requirements.txt

# Show what we're about to install
RUN cat requirements.txt

# Install ALL packages directly
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    streamlit>=1.28.0 \
    edge-tts>=6.1.9 \
    pygame>=2.5.0

# Verify installations
RUN python -c "import edge_tts; print('edge_tts installed')" && \
    python -c "import pygame; print('pygame installed')" && \
    python -c "import streamlit; print('streamlit version:', streamlit.__version__)"

# Copy application code (excluding requirements.txt since we created it)
COPY app.py .
COPY lists/ ./lists/

# Create required directories
RUN mkdir -p tts_cache

EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
