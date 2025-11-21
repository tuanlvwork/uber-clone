#!/bin/bash

# Uber Clone - Build Images Script
# This script builds all Docker images for Kubernetes deployment

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "  Building Docker Images"
echo "=========================================="
echo ""

# Point Docker to Minikube's daemon
echo -e "${YELLOW}Configuring Docker to use Minikube's daemon...${NC}"
eval $(minikube docker-env)
echo -e "${GREEN}✓ Docker configured${NC}"
echo ""

# Build microservices image
echo -e "${YELLOW}Building uber-clone:latest...${NC}"
docker build -t uber-clone:latest -f Dockerfile .
echo -e "${GREEN}✓ Built uber-clone:latest${NC}"
echo ""

# Build frontend image
echo -e "${YELLOW}Building uber-clone-frontend:latest...${NC}"
docker build -t uber-clone-frontend:latest -f Dockerfile.frontend .
echo -e "${GREEN}✓ Built uber-clone-frontend:latest${NC}"
echo ""

# Pull external images
echo -e "${YELLOW}Pulling external images...${NC}"
docker pull confluentinc/cp-kafka:7.5.0
docker pull postgres:13
docker pull provectuslabs/kafka-ui:latest
docker pull prom/prometheus:latest
docker pull grafana/grafana:latest
docker pull busybox:1.35
echo -e "${GREEN}✓ All images ready${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}  Build Complete!${NC}"
echo "=========================================="
echo ""
echo "Available images:"
docker images | grep -E "uber-clone|kafka|postgres|grafana|prometheus"
