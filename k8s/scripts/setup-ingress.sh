#!/bin/bash

# Uber Clone - Ingress Setup Script
# This script enables and configures Ingress for easy access to all services

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "  Setting up Ingress for Uber Clone"
echo "=========================================="
echo ""

# Check if minikube is running
if ! minikube status > /dev/null 2>&1; then
    echo -e "${RED}Error: Minikube is not running${NC}"
    echo "Start it with: minikube start"
    exit 1
fi

# Enable ingress addon
echo -e "${YELLOW}Enabling Minikube Ingress addon...${NC}"
minikube addons enable ingress
echo -e "${GREEN}✓ Ingress addon enabled${NC}"
echo ""

# Wait for ingress controller to be ready
echo -e "${YELLOW}Waiting for Ingress controller to be ready...${NC}"
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

echo -e "${GREEN}✓ Ingress controller is ready${NC}"
echo ""

# Apply ingress configuration
echo -e "${YELLOW}Applying Ingress configuration...${NC}"
kubectl apply -f k8s/50-ingress.yaml
echo -e "${GREEN}✓ Ingress configured${NC}"
echo ""

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Add entry to /etc/hosts (optional)
echo -e "${YELLOW}Adding entry to /etc/hosts (requires sudo)...${NC}"
echo ""
echo "This will add: $MINIKUBE_IP uber-clone.local"
echo -e "${YELLOW}Press Enter to continue or Ctrl+C to skip${NC}"
read

if ! grep -q "uber-clone.local" /etc/hosts 2>/dev/null; then
    echo "$MINIKUBE_IP uber-clone.local" | sudo tee -a /etc/hosts
    echo -e "${GREEN}✓ Added to /etc/hosts${NC}"
else
    echo -e "${YELLOW}Entry already exists in /etc/hosts${NC}"
    # Update the IP if it changed
    sudo sed -i '' "s/.*uber-clone.local/$MINIKUBE_IP uber-clone.local/" /etc/hosts
    echo -e "${GREEN}✓ Updated in /etc/hosts${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  Ingress Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Access your services at:"
echo "  • Frontend:       http://uber-clone.local/"
echo "  • API Gateway:    http://uber-clone.local/api/"
echo "  • Kafka UI:       http://uber-clone.local/kafka-ui/"
echo "  • Grafana:        http://uber-clone.local/grafana/"
echo "  • Prometheus:     http://uber-clone.local/prometheus/"
echo ""
echo "Or directly via IP:"
echo "  • Frontend:       http://$MINIKUBE_IP/"
echo ""
echo "View Ingress status:"
echo "  kubectl get ingress -n uber-clone"
echo ""
