FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libmagic1 \
    ghostscript \
    poppler-utils \
    libheif-dev \
    imagemagick \
    libmagickwand-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with specific NumPy version first to avoid compatibility issues
RUN pip install --no-cache-dir numpy==1.24.3
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Default port (can be overridden by environment)
ENV PORT=5000
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application
CMD cd /app && gunicorn --bind 0.0.0.0:$PORT app.app:app 