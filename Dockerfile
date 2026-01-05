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

# Copy requirements first
COPY requirements.txt .

# Install pip packages directly (bypass potential cache issues)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir streamlit>=1.28.0 edge-tts>=6.1.9 pygame>=2.5.0

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p lists tts_cache

EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
