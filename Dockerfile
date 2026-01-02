FROM python:3.9-slim

# Install system dependencies for pygame and audio
RUN apt-get update && apt-get install -y echo     gcc echo     g++ echo     libsdl2-dev echo     libsdl2-mixer-dev echo     libsdl2-ttf-dev echo     libportmidi-dev echo     libswscale-dev echo     libavformat-dev echo     libavcodec-dev echo     zlib1g-dev echo     libfreetype6-dev echo     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories if they don't exist
RUN mkdir -p lists tts_cache

# Expose Streamlit port
EXPOSE 7860

# Health check
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health || exit 1

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
