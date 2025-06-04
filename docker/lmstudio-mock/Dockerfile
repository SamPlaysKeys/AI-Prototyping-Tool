FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies
RUN pip install fastapi uvicorn[standard] pydantic

# Copy mock service
COPY mock_lmstudio.py /app/

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 mockuser
USER mockuser

# Expose port
EXPOSE 1234

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:1234/v1/models || exit 1

# Run the mock service
CMD ["python", "-m", "uvicorn", "mock_lmstudio:app", "--host", "0.0.0.0", "--port", "1234"]
