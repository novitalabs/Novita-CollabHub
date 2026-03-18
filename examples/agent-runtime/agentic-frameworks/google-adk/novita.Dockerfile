FROM novitalabs/code-interpreter:latest

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install from requirements file (pip requirements format: .txt or .in)
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Copy application code after dependency installation
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV NOVITA_AGENT_NAME=google-adk
ENV NOVITA_AGENT_VERSION=1.0.0

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/ping || exit 1

# Run the agent using module path
CMD ["python", "-m", "app"]
