# FastMCP Denodo Server
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .
COPY main.py .

# Copy .env file if it exists
COPY .env* ./

# Expose the default port
EXPOSE 8080

# Set environment variables with defaults
ENV MCP_SERVER_HOST=0.0.0.0
ENV MCP_SERVER_PORT=8080
ENV DENODO_AI_SDK_ENDPOINT=http://localhost:8008
ENV DENODO_AI_SDK_USER=admin
ENV DENODO_AI_SDK_PASSWORD=admin
ENV DENODO_AI_SDK_VERIFY_SSL=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8080/health', timeout=5)" || exit 1

# Run the FastMCP server
CMD ["python", "main.py"]
