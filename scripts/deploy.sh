#!/bin/bash
#
# CT-X Deployment Script
# One-command deployment for production
#

set -e  # Exit on error

echo "🚀 Deploying CT-X v2.0.0..."
echo "=========================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="${DOCKER_REGISTRY:-your-registry}"
IMAGE_NAME="ct-x-inference"
VERSION="v2.0.0"
NAMESPACE="ct-x-production"

# Functions
log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Step 1: Build Docker image
echo ""
echo "Step 1: Building Docker image..."
if docker build -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest .; then
    log_success "Docker image built successfully"
else
    log_error "Docker build failed"
    exit 1
fi

# Step 2: Tag and push to registry (optional)
if [ -n "$DOCKER_REGISTRY" ]; then
    echo ""
    echo "Step 2: Pushing to registry..."
    docker tag ${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:${VERSION}
    docker tag ${IMAGE_NAME}:latest ${REGISTRY}/${IMAGE_NAME}:latest

    if docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION} && \
       docker push ${REGISTRY}/${IMAGE_NAME}:latest; then
        log_success "Images pushed to registry"
    else
        log_warning "Failed to push to registry (continuing anyway)"
    fi
else
    log_warning "DOCKER_REGISTRY not set, skipping push"
fi

# Step 3: Run benchmarks
echo ""
echo "Step 3: Running benchmarks..."
if [ -d "/models/ct-x-70b" ]; then
    if python benchmark.py --model-path /models/ct-x-70b --output benchmark-results.txt; then
        log_success "Benchmarks completed"
        cat benchmark-results.txt
    else
        log_warning "Benchmarks failed (continuing anyway)"
    fi
else
    log_warning "Model not found at /models/ct-x-70b, skipping benchmarks"
fi

# Step 4: Deploy to Kubernetes (if available)
echo ""
echo "Step 4: Deploying to Kubernetes..."
if command -v kubectl &> /dev/null; then
    # Create namespace if it doesn't exist
    kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

    # Apply deployment
    if kubectl apply -f kubernetes-deployment.yaml; then
        log_success "Kubernetes resources applied"
    else
        log_error "Kubernetes deployment failed"
        exit 1
    fi

    # Wait for pods to be ready
    echo "Waiting for pods to be ready..."
    if kubectl wait --for=condition=ready pod \
        -l app=ct-x \
        -n ${NAMESPACE} \
        --timeout=300s; then
        log_success "Pods are ready"
    else
        log_warning "Pods not ready after 5 minutes"
    fi

    # Get service endpoint
    echo ""
    echo "Service information:"
    kubectl get svc ct-x-service -n ${NAMESPACE}

else
    log_warning "kubectl not found, skipping Kubernetes deployment"

    # Fall back to Docker Compose
    echo ""
    echo "Falling back to Docker Compose..."
    if docker-compose up -d; then
        log_success "Docker Compose deployment started"
    else
        log_error "Docker Compose deployment failed"
        exit 1
    fi
fi

# Step 5: Start monitoring dashboard
echo ""
echo "Step 5: Starting monitoring dashboard..."
if nohup python dashboard.py > dashboard.log 2>&1 & then
    DASHBOARD_PID=$!
    log_success "Dashboard started (PID: ${DASHBOARD_PID})"
    echo "Dashboard logs: tail -f dashboard.log"
else
    log_warning "Failed to start dashboard"
fi

# Step 6: Verify deployment
echo ""
echo "Step 6: Verifying deployment..."
sleep 5  # Give services time to start

# Check health endpoint
if command -v kubectl &> /dev/null; then
    # Kubernetes deployment
    API_ENDPOINT=$(kubectl get svc ct-x-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -z "$API_ENDPOINT" ]; then
        API_ENDPOINT="localhost:8000"
    fi
else
    # Docker Compose deployment
    API_ENDPOINT="localhost:8000"
fi

echo "Testing API endpoint: http://${API_ENDPOINT}/health"
if curl -s "http://${API_ENDPOINT}/health" > /dev/null 2>&1; then
    log_success "API is responding"
else
    log_warning "API not responding yet (may need more time)"
fi

# Final summary
echo ""
echo "================================================================"
echo "✅ Deployment Complete"
echo "================================================================"
echo ""
echo "API endpoint:       http://${API_ENDPOINT}"
echo "Dashboard:          http://localhost:5000"
echo "Kubernetes namespace: ${NAMESPACE}"
echo ""
echo "Quick commands:"
echo "  kubectl get pods -n ${NAMESPACE}"
echo "  kubectl logs -f deployment/ct-x-inference -n ${NAMESPACE}"
echo "  curl http://${API_ENDPOINT}/health"
echo ""
echo "To stop:"
if command -v kubectl &> /dev/null; then
    echo "  kubectl delete namespace ${NAMESPACE}"
else
    echo "  docker-compose down"
fi
echo ""
log_success "CT-X is now running!"
