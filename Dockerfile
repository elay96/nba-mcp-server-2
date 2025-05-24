# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that your app will run on (Railway will set this dynamically)
# ENV PORT=8000 # No longer strictly needed here as Railway injects it
EXPOSE ${PORT:-8000} # Expose the port, default to 8000 if PORT is not set

# Add healthcheck (optional but good practice for Railway)
# Note: SSE endpoints might not respond to simple HTTP GET for healthcheck
# Depending on FastMCP's SSE implementation, this might need adjustment or removal
# if it causes issues.
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:${PORT}/sse || exit 1 # Attempt to check the SSE path

# Run the SSE MCP server when the container launches
CMD ["python", "nba_mcp_sse_server.py"]

# docker build -t nba_server .
# docker run -p 4000:5000 nba_server

