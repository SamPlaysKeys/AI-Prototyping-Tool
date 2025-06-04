# Docker Deployment Guide

This guide covers containerization and deployment of the AI Prototyping Tool using Docker and Docker Compose.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Building Containers](#building-containers)
- [Running with Docker Compose](#running-with-docker-compose)
- [Configuration](#configuration)
- [Services Overview](#services-overview)
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- At least 2GB of available RAM
- At least 1GB of available disk space

### Installing Docker

**macOS:**
```bash
brew install docker docker-compose
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin
```

**Windows:**
Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd AI-Prototyping-Tool
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Web interface: http://localhost:8000
   - LM Studio Mock API: http://localhost:1234
   - Health check: http://localhost:8000/health

4. **Stop all services:**
   ```bash
   docker-compose down
   ```

## Building Containers

### Build Web Application Image

```bash
# Build the main application
docker build -t ai-prototyping-tool:latest .

# Build with specific target
docker build --target production -t ai-prototyping-tool:prod .
```

### Build Mock LM Studio Service

```bash
# Build the mock service
docker build -t lmstudio-mock:latest ./docker/lmstudio-mock/
```

### Build All Services

```bash
# Build all services defined in docker-compose.yml
docker-compose build

# Build with no cache (clean build)
docker-compose build --no-cache
```

## Running with Docker Compose

### Basic Usage

```bash
# Start all services in background
docker-compose up -d

# Start specific services
docker-compose up -d ai-prototyping-web lmstudio-mock

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f ai-prototyping-web

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Development Mode

```bash
# Run with live reload and debugging
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Production Mode with Nginx

```bash
# Start with production profile
docker-compose --profile production up -d
```

### With Monitoring

```bash
# Start with monitoring stack (Prometheus + Grafana)
docker-compose --profile monitoring up -d
```

## Configuration

### Environment Variables

The application can be configured using environment variables:

```bash
# Core application settings
AIPROTO_APP_ENVIRONMENT=development
AIPROTO_APP_DEBUG=false
AIPROTO_APP_VERSION=1.0.0

# Server configuration
AIPROTO_SERVER_HOST=0.0.0.0
AIPROTO_SERVER_PORT=8000
AIPROTO_SERVER_WORKERS=1

# LM Studio configuration
AIPROTO_LM_STUDIO_BASE_URL=http://lmstudio-mock:1234
AIPROTO_LM_STUDIO_CONNECTION_TIMEOUT=5.0

# Logging configuration
AIPROTO_LOGGING_LEVEL=INFO
AIPROTO_LOGGING_FORMAT=structured
```

### Docker Compose Override

Create a `docker-compose.override.yml` file for local customizations:

```yaml
version: '3.8'

services:
  ai-prototyping-web:
    environment:
      - AIPROTO_APP_DEBUG=true
      - AIPROTO_LOGGING_LEVEL=DEBUG
    volumes:
      - ./src:/app/src:ro  # Mount source for development
    ports:
      - "8001:8000"  # Use different port
```

## Services Overview

### Main Services

| Service | Port | Description |
|---------|------|-------------|
| ai-prototyping-web | 8000 | Main web application |
| lmstudio-mock | 1234 | Mock LM Studio API for testing |

### Optional Services

| Service | Port | Description | Profile |
|---------|------|-------------|----------|
| redis | 6379 | Caching and session storage | default |
| nginx | 80, 443 | Reverse proxy and SSL termination | production |
| prometheus | 9090 | Metrics collection | monitoring |
| grafana | 3000 | Metrics visualization | monitoring |

### Health Checks

All services include health checks:

```bash
# Check service health
docker-compose ps

# Check specific service health
docker inspect ai-prototyping-web --format='{{.State.Health.Status}}'
```

## Development Setup

### Live Development with Volume Mounts

Create `docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  ai-prototyping-web:
    environment:
      - AIPROTO_APP_DEBUG=true
      - AIPROTO_LOGGING_LEVEL=DEBUG
      - AIPROTO_SERVER_RELOAD=true
    volumes:
      - ./src:/app/src:ro
      - ./web:/app/web:ro
      - ./templates:/app/templates:ro
    command: >
      python -m uvicorn web.app:app
      --host 0.0.0.0
      --port 8000
      --reload
      --log-level debug
```

### Running Tests in Container

```bash
# Run tests
docker-compose exec ai-prototyping-web python -m pytest

# Run tests with coverage
docker-compose exec ai-prototyping-web python -m pytest --cov=src

# Run specific test file
docker-compose exec ai-prototyping-web python -m pytest tests/test_specific.py
```

### Debugging

```bash
# Access container shell
docker-compose exec ai-prototyping-web bash

# View application logs
docker-compose logs -f ai-prototyping-web

# Monitor resource usage
docker stats
```

## Production Deployment

### Security Considerations

1. **Use non-root user:** Already configured in Dockerfiles
2. **Network isolation:** Services communicate through internal network
3. **Secrets management:** Use Docker secrets or external secret management
4. **SSL/TLS:** Configure with nginx service

### Resource Limits

Add resource limits to `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  ai-prototyping-web:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

### Scaling

```bash
# Scale web service to 3 replicas
docker-compose up -d --scale ai-prototyping-web=3

# Use with load balancer
docker-compose --profile production up -d
```

### Backup and Restore

```bash
# Backup volumes
docker run --rm -v ai-prototyping-redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v ai-prototyping-redis-data:/data -v $(pwd):/backup alpine tar xzf /backup/redis-backup.tar.gz -C /data
```

## Monitoring

### Prometheus Metrics

Start monitoring stack:

```bash
docker-compose --profile monitoring up -d
```

Access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin123)

### Application Metrics

The application exposes metrics at `/metrics` endpoint:

```bash
curl http://localhost:8000/metrics
```

### Log Aggregation

View aggregated logs:

```bash
# Follow all service logs
docker-compose logs -f

# Filter logs by service
docker-compose logs -f ai-prototyping-web | grep ERROR

# Export logs
docker-compose logs --no-color > application.log
```

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check what's using the port
   lsof -i :8000

   # Use different ports in docker-compose.override.yml
   ```

2. **Permission issues:**
   ```bash
   # Fix volume permissions
   sudo chown -R 1000:1000 ./output ./logs
   ```

3. **Memory issues:**
   ```bash
   # Check container memory usage
   docker stats

   # Increase Docker memory limit in Docker Desktop settings
   ```

4. **Network connectivity:**
   ```bash
   # Test service connectivity
   docker-compose exec ai-prototyping-web curl http://lmstudio-mock:1234/health
   ```

5. **Build failures:**
   ```bash
   # Clean build without cache
   docker-compose build --no-cache

   # Remove old images
   docker system prune -a
   ```

### Diagnostic Commands

```bash
# Check service status
docker-compose ps

# View container details
docker inspect ai-prototyping-web

# Check logs for errors
docker-compose logs ai-prototyping-web | grep -i error

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:1234/health

# Check network connectivity
docker network ls
docker network inspect ai-prototyping-network
```

### Performance Tuning

1. **Optimize Docker build:**
   - Use multi-stage builds (already implemented)
   - Optimize layer caching
   - Minimize image size

2. **Container resources:**
   - Monitor CPU and memory usage
   - Adjust resource limits as needed
   - Use appropriate restart policies

3. **Network optimization:**
   - Use internal networks for service communication
   - Consider connection pooling for databases

### Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify health checks: `docker-compose ps`
3. Test individual services: `curl http://localhost:8000/health`
4. Check Docker and Docker Compose versions
5. Review the troubleshooting section above

For additional support, please refer to the main project documentation or create an issue in the project repository.
