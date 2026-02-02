# Dockerfile for Code Review Assistant
# Optimized for Google Cloud Run deployment

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create Streamlit config directory
RUN mkdir -p ~/.streamlit

# Expose port for Cloud Run
EXPOSE 8080

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health || exit 1

# Run Streamlit
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
