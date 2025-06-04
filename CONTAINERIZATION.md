# AI Prototyping Tool - Containerization & Deployment

This document provides an overview of the containerization and deployment options for the AI Prototyping Tool.

## 🚀 Quick Start

### Using Docker Compose (Recommended for Local Development)

```bash
# Start all services
docker-compose up -d

# Access the application
open http://localhost:8000

# Stop all services
docker-compose down
```

### Using the Build Script

```bash
# Build and test containers
./scripts/build-containers.sh

# Build and push to registry
./scripts/build-containers.sh --registry your-registry.com/username --push
```

## 📁 Project Structure

```
.
├── Dockerfile                          # Main web application container
├── docker-compose.yml                  # Complete stack with mock services
├── .dockerignore                       # Docker build context exclusions
├── docker/
│   └── lmstudio-mock/
│       ├── Dockerfile                  # Mock LM Studio API service
│       └── mock_lmstudio.py           # Mock service implementation
├── k8s/                                # Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── web-deployment.yaml
│   ├── lmstudio-mock-deployment.yaml
│   ├── services.yaml
│   └── ingress.yaml
├── helm/                               # Helm chart
│   └── ai-prototyping-tool/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── scripts/
│   └── build-containers.sh            # Build and test script
└── docs/
    ├── DOCKER_DEPLOYMENT.md            # Detailed Docker guide
    └── KUBERNETES_DEPLOYMENT.md        # Detailed Kubernetes guide
```

## 🐳 Container Images

### Web Application (`ai-prototyping-tool:1.0.0`)
- **Base**: Python 3.11 slim
- **Framework**: FastAPI with Uvicorn
- **Features**:
  - Multi-stage build for optimization
  - Non-root user security
  - Health checks
  - Structured logging
  - Configuration via environment variables

### Mock LM Studio (`lmstudio-mock:1.0.0`)
- **Base**: Python 3.11 slim
- **Purpose**: Testing and development without real LM Studio
- **Features**:
  - OpenAI-compatible API
  - Multiple mock models
  - Realistic response simulation
  - Health monitoring

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `AIPROTO_APP_ENVIRONMENT` | Application environment | `development` |
| `AIPROTO_APP_DEBUG` | Enable debug mode | `false` |
| `AIPROTO_LM_STUDIO_BASE_URL` | LM Studio API URL | `http://localhost:1234` |
| `AIPROTO_LOGGING_LEVEL` | Log level | `INFO` |
| `AIPROTO_SERVER_HOST` | Server bind address | `0.0.0.0` |
| `AIPROTO_SERVER_PORT` | Server port | `8000` |

### Docker Compose Profiles

```bash
# Default: web app + mock LM Studio + Redis
docker-compose up -d

# Production: + Nginx reverse proxy
docker-compose --profile production up -d

# Monitoring: + Prometheus + Grafana
docker-compose --profile monitoring up -d
```

## ☸️ Kubernetes Deployment

### Quick Deploy with kubectl

```bash
# Deploy all components
kubectl apply -f k8s/

# Check status
kubectl get pods -n ai-prototyping-tool

# Access via port forward
kubectl port-forward -n ai-prototyping-tool service/ai-prototyping-web-service 8000:8000
```

### Deploy with Helm

```bash
# Install with default values
helm install ai-prototyping-tool ./helm/ai-prototyping-tool \
  --create-namespace \
  --namespace ai-prototyping-tool

# Install with custom configuration
helm install ai-prototyping-tool ./helm/ai-prototyping-tool \
  --create-namespace \
  --namespace ai-prototyping-tool \
  --set web.replicaCount=3 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=ai-prototyping.example.com
```

## 🏗️ Building Images

### Manual Build

```bash
# Build web application
docker build -t ai-prototyping-tool:1.0.0 .

# Build mock LM Studio
docker build -t lmstudio-mock:1.0.0 ./docker/lmstudio-mock/
```

### Using Build Script

```bash
# Build and test locally
./scripts/build-containers.sh

# Build for specific registry
./scripts/build-containers.sh --registry docker.io/username --tag latest

# Build and push to registry
./scripts/build-containers.sh --registry docker.io/username --push

# Skip tests during build
./scripts/build-containers.sh --no-tests
```

## 🔍 Health Monitoring

### Health Check Endpoints

| Service | Endpoint | Port |
|---------|----------|------|
| Web App | `/health` | 8000 |
| Mock LM Studio | `/health` | 1234 |
| Web App Metrics | `/metrics` | 8000 |

### Testing Health

```bash
# Test web application
curl http://localhost:8000/health

# Test mock LM Studio
curl http://localhost:1234/health

# Test LM Studio models
curl http://localhost:1234/v1/models
```

## 🛡️ Security Features

- **Non-root containers**: All containers run as non-root users
- **Read-only root filesystem**: Where possible
- **Dropped capabilities**: All unnecessary Linux capabilities removed
- **Security contexts**: Kubernetes security policies applied
- **Network policies**: Kubernetes network isolation (optional)
- **Resource limits**: CPU and memory limits enforced

## 📊 Monitoring & Observability

### Prometheus Metrics
- Application performance metrics
- Request/response statistics
- Health check status
- Custom business metrics

### Structured Logging
- JSON-formatted logs
- Correlation IDs for request tracing
- Configurable log levels
- Centralized log collection ready

### Health Checks
- Kubernetes liveness probes
- Kubernetes readiness probes
- Docker health checks
- Custom health endpoints

## 🔄 Development Workflow

### Local Development

1. **Start services**:
   ```bash
   docker-compose up -d
   ```

2. **Make changes to code**

3. **Rebuild and test**:
   ```bash
   ./scripts/build-containers.sh
   docker-compose up -d --build
   ```

4. **View logs**:
   ```bash
   docker-compose logs -f ai-prototyping-web
   ```

### Production Deployment

1. **Build and push images**:
   ```bash
   ./scripts/build-containers.sh --registry your-registry.com/project --push
   ```

2. **Deploy to Kubernetes**:
   ```bash
   helm upgrade --install ai-prototyping-tool ./helm/ai-prototyping-tool \
     --namespace ai-prototyping-tool \
     --set web.image.repository=your-registry.com/project/ai-prototyping-tool
   ```

3. **Monitor deployment**:
   ```bash
   kubectl rollout status deployment/ai-prototyping-web -n ai-prototyping-tool
   ```

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**:
   ```bash
   # Change ports in docker-compose.override.yml
   services:
     ai-prototyping-web:
       ports:
         - "8001:8000"
   ```

2. **Memory issues**:
   ```bash
   # Check container memory usage
   docker stats

   # Increase Docker memory limit
   ```

3. **Image build failures**:
   ```bash
   # Clean build without cache
   docker build --no-cache -t ai-prototyping-tool:1.0.0 .
   ```

4. **Service connectivity**:
   ```bash
   # Test internal network
   docker-compose exec ai-prototyping-web curl http://lmstudio-mock:1234/health
   ```

### Useful Commands

```bash
# View all containers
docker-compose ps

# Follow logs for all services
docker-compose logs -f

# Execute command in container
docker-compose exec ai-prototyping-web bash

# Restart specific service
docker-compose restart ai-prototyping-web

# Rebuild and restart
docker-compose up -d --build ai-prototyping-web
```

## 📚 Additional Documentation

- **[Docker Deployment Guide](docs/DOCKER_DEPLOYMENT.md)** - Detailed Docker setup and configuration
- **[Kubernetes Deployment Guide](docs/KUBERNETES_DEPLOYMENT.md)** - Complete Kubernetes deployment instructions
- **[Main README](README.md)** - Project overview and features

## 🤝 Contributing

When contributing containerization improvements:

1. Test locally with `./scripts/build-containers.sh`
2. Update documentation if adding new features
3. Follow security best practices
4. Test both Docker Compose and Kubernetes deployments
5. Update version tags appropriately

## 📄 License

This project is licensed under the MIT License - see the main project README for details.
