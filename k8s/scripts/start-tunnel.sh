#!/bin/bash

# Uber Clone - Minikube Tunnel Starter
# This script starts minikube tunnel to make services accessible on localhost

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "  Starting Minikube Tunnel"
echo "=========================================="
echo ""

# Check if minikube is running
if ! minikube status > /dev/null 2>&1; then
    echo -e "${RED}Error: Minikube is not running${NC}"
    echo "Start it with: minikube start"
    exit 1
fi

echo -e "${YELLOW}Starting tunnel (requires sudo password)...${NC}"
echo ""
echo "This will make all services accessible at localhost:"
echo "  • Frontend:       http://localhost:30080"
echo "  • API Gateway:    http://localhost:30001"
echo "  • Kafka UI:       http://localhost:30090"
echo "  • Grafana:        http://localhost:30030"
echo "  • Prometheus:     http://localhost:30091"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the tunnel${NC}"
echo ""

# Start tunnel (will ask for sudo password)
minikube tunnel
