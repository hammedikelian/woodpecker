FROM python:3.11-slim

# Install system dependencies including ffmpeg for audio conversion
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Vosk French model
RUN wget -q https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip \
    && unzip vosk-model-small-fr-0.22.zip \
    && rm vosk-model-small-fr-0.22.zip

# Copy application code
COPY . .

# Expose port
EXPOSE 5001

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]
