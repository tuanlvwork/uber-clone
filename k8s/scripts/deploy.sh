#!/bin/bash

# Uber Clone - Kubernetes Deployment Script
# This script deploys the complete Uber Clone application to Minikube

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Uber Clone - Kubernetes Deployment"
echo "=========================================="
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v minikube &> /dev/null; then
    echo -e "${RED}Error: minikube is not installed${NC}"
    echo "Install with: brew install minikube"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    echo "Install with: brew install kubectl"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: docker is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites installed${NC}"
echo ""

# Check if Minikube is running
echo -e "${YELLOW}Checking Minikube status...${NC}"
if ! minikube status &> /dev/null; then
    echo -e "${YELLOW}Starting Minikube...${NC}"
    minikube start --cpus=2 --memory=4096 --disk-size=20g --kubernetes-version=v1.30.0
    echo -e "${GREEN}✓ Minikube started${NC}"
else
    echo -e "${GREEN}✓ Minikube is already running${NC}"
fi
echo ""

# Point Docker to Minikube's daemon
echo -e "${YELLOW}Configuring Docker to use Minikube's daemon...${NC}"
eval $(minikube docker-env)
echo -e "${GREEN}✓ Docker configured${NC}"
echo ""

# Build images
echo -e "${YELLOW}Building Docker images...${NC}"

echo "Building uber-clone:latest..."
docker build -t uber-clone:latest -f Dockerfile .
echo -e "${GREEN}✓ Built uber-clone:latest${NC}"

echo "Building uber-clone-frontend:latest..."
docker build -t uber-clone-frontend:latest -f Dockerfile.frontend .
echo -e "${GREEN}✓ Built uber-clone-frontend:latest${NC}"
echo ""

# Pull required images
echo -e "${YELLOW}Pulling external images...${NC}"
docker pull confluentinc/cp-kafka:7.5.0
docker pull postgres:13
docker pull provectuslabs/kafka-ui:latest
docker pull prom/prometheus:latest
docker pull grafana/grafana:latest
echo -e "${GREEN}✓ All images ready${NC}"
echo ""

# Deploy to Kubernetes
echo -e "${YELLOW}Deploying to Kubernetes...${NC}"

echo "Creating namespace..."
kubectl apply -f k8s/00-namespace.yaml

echo "Creating ConfigMap and Secrets..."
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secrets.yaml

echo "Deploying infrastructure (Kafka, PostgreSQL)..."
kubectl apply -f k8s/10-kafka.yaml
kubectl apply -f k8s/11-postgres.yaml
kubectl apply -f k8s/12-kafka-ui.yaml

echo "Waiting for infrastructure to be ready..."
kubectl wait --for=condition=ready pod -l app=kafka -n uber-clone --timeout=120s
kubectl wait --for=condition=ready pod -l app=postgres -n uber-clone --timeout=120s

echo "Deploying microservices..."
kubectl apply -f k8s/20-api-gateway.yaml
kubectl apply -f k8s/21-ride-service.yaml
kubectl apply -f k8s/22-driver-service.yaml
kubectl apply -f k8s/23-matching-service.yaml
kubectl apply -f k8s/24-location-service.yaml


echo "Deploying frontend..."
kubectl apply -f k8s/30-frontend.yaml

echo "Deploying monitoring stack..."
kubectl apply -f k8s/40-prometheus.yaml
kubectl apply -f k8s/41-grafana.yaml

echo -e "${GREEN}✓ All resources deployed${NC}"
echo ""

# Wait for deployments
echo -e "${YELLOW}Waiting for all pods to be ready (this may take 2-3 minutes)...${NC}"
kubectl wait --for=condition=ready pod --all -n uber-clone --timeout=300s || true
echo ""

# Show status
echo "=========================================="
echo -e "${GREEN}  Deployment Complete!${NC}"
echo "=========================================="
echo ""

MINIKUBE_IP=$(minikube ip)

echo "Access the application:"
echo "  • Frontend:       http://$MINIKUBE_IP:30080"
echo "  • Rider App:      http://$MINIKUBE_IP:30080/rider.html"
echo "  • Driver App:     http://$MINIKUBE_IP:30080/driver.html"
echo "  • Kafka UI:       http://$MINIKUBE_IP:30090"
echo "  • Grafana:        http://$MINIKUBE_IP:30030 (admin/admin)"
echo ""

echo "Or use minikube service commands (Recommended for macOS):"
echo "  minikube service frontend -n uber-clone"
echo "  minikube service kafka-ui -n uber-clone"
echo "  minikube service grafana -n uber-clone"
echo ""

echo "Check status:"
echo "  kubectl get pods -n uber-clone"
echo "  kubectl logs -f deployment/api-gateway -n uber-clone"
echo ""

echo "To delete everything:"
echo "  ./k8s/scripts/cleanup.sh"
echo ""
echo "=========================================="
