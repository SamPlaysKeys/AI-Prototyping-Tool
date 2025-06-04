#!/bin/bash

# AI Prototyping Tool - Container Build and Test Script
# This script builds the Docker containers and tests them locally

set -e  # Exit on any error

# Configuration
IMAGE_TAG="1.0.0"
REGISTRY=""
PUSH_TO_REGISTRY=false
RUN_TESTS=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --push)
            PUSH_TO_REGISTRY=true
            shift
            ;;
        --no-tests)
            RUN_TESTS=false
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --registry REGISTRY  Docker registry to use (e.g., docker.io/username)"
            echo "  --tag TAG            Image tag to use (default: 1.0.0)"
            echo "  --push               Push images to registry after building"
            echo "  --no-tests           Skip running tests"
            echo "  -h, --help           Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set image names
if [[ -n "$REGISTRY" ]]; then
    WEB_IMAGE="${REGISTRY}/ai-prototyping-tool:${IMAGE_TAG}"
    MOCK_IMAGE="${REGISTRY}/lmstudio-mock:${IMAGE_TAG}"
else
    WEB_IMAGE="ai-prototyping-tool:${IMAGE_TAG}"
    MOCK_IMAGE="lmstudio-mock:${IMAGE_TAG}"
fi

log_info "Starting container build process"
log_info "Web application image: $WEB_IMAGE"
log_info "Mock LM Studio image: $MOCK_IMAGE"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    log_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build web application image
log_info "Building web application image..."
if docker build -t "$WEB_IMAGE" .; then
    log_success "Web application image built successfully"
else
    log_error "Failed to build web application image"
    exit 1
fi

# Build mock LM Studio image
log_info "Building mock LM Studio image..."
if docker build -t "$MOCK_IMAGE" ./docker/lmstudio-mock/; then
    log_success "Mock LM Studio image built successfully"
else
    log_error "Failed to build mock LM Studio image"
    exit 1
fi

# Run tests if requested
if [[ "$RUN_TESTS" == "true" ]]; then
    log_info "Running container tests..."

    # Test web application container
    log_info "Testing web application container..."
    CONTAINER_ID=$(docker run -d -p 8000:8000 "$WEB_IMAGE")

    # Wait for container to start
    sleep 10

    # Test health endpoint
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Web application health check passed"
    else
        log_error "Web application health check failed"
        docker logs "$CONTAINER_ID"
        docker stop "$CONTAINER_ID" > /dev/null
        docker rm "$CONTAINER_ID" > /dev/null
        exit 1
    fi

    # Stop and remove test container
    docker stop "$CONTAINER_ID" > /dev/null
    docker rm "$CONTAINER_ID" > /dev/null

    # Test mock LM Studio container
    log_info "Testing mock LM Studio container..."
    MOCK_CONTAINER_ID=$(docker run -d -p 1234:1234 "$MOCK_IMAGE")

    # Wait for container to start
    sleep 5

    # Test health endpoint
    if curl -f http://localhost:1234/health > /dev/null 2>&1; then
        log_success "Mock LM Studio health check passed"
    else
        log_error "Mock LM Studio health check failed"
        docker logs "$MOCK_CONTAINER_ID"
        docker stop "$MOCK_CONTAINER_ID" > /dev/null
        docker rm "$MOCK_CONTAINER_ID" > /dev/null
        exit 1
    fi

    # Test models endpoint
    if curl -f http://localhost:1234/v1/models > /dev/null 2>&1; then
        log_success "Mock LM Studio models endpoint test passed"
    else
        log_warning "Mock LM Studio models endpoint test failed"
    fi

    # Stop and remove test container
    docker stop "$MOCK_CONTAINER_ID" > /dev/null
    docker rm "$MOCK_CONTAINER_ID" > /dev/null

    log_success "All container tests passed!"
fi

# Push to registry if requested
if [[ "$PUSH_TO_REGISTRY" == "true" ]]; then
    if [[ -z "$REGISTRY" ]]; then
        log_error "Registry not specified. Use --registry option to specify registry."
        exit 1
    fi

    log_info "Pushing images to registry..."

    if docker push "$WEB_IMAGE"; then
        log_success "Web application image pushed successfully"
    else
        log_error "Failed to push web application image"
        exit 1
    fi

    if docker push "$MOCK_IMAGE"; then
        log_success "Mock LM Studio image pushed successfully"
    else
        log_error "Failed to push mock LM Studio image"
        exit 1
    fi
fi

# Show image information
log_info "Image information:"
echo "Web Application:"
docker images "$WEB_IMAGE" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
echo "Mock LM Studio:"
docker images "$MOCK_IMAGE" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"

log_success "Container build process completed successfully!"

# Show next steps
echo ""
log_info "Next steps:"
echo "1. Start the application stack:"
echo "   docker-compose up -d"
echo "2. Access the web interface:"
echo "   http://localhost:8000"
echo "3. View logs:"
echo "   docker-compose logs -f"
echo "4. Stop the stack:"
echo "   docker-compose down"

if [[ "$PUSH_TO_REGISTRY" == "true" ]]; then
    echo "5. Deploy to Kubernetes:"
    echo "   kubectl apply -f k8s/"
    echo "   or"
    echo "   helm install ai-prototyping-tool ./helm/ai-prototyping-tool"
fi
