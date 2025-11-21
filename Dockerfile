# Multi-stage build for Uber-Clone microservices
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/ ./services/
COPY models/ ./models/
COPY scripts/ ./scripts/

# Create logs directory
RUN mkdir -p logs

# Default command (will be overridden by specific service)
CMD ["python", "-u"]
