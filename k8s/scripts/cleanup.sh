#!/bin/bash

# Uber Clone - Kubernetes Cleanup Script
# This script removes all Kubernetes resources

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Uber Clone - Kubernetes Cleanup"
echo "=========================================="
echo ""

echo -e "${YELLOW}This will delete all Uber Clone resources from Kubernetes${NC}"
read -p "Are you sure? (yes/no): " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo -e "${YELLOW}Deleting all resources...${NC}"

# Delete namespace (this will delete everything inside)
kubectl delete namespace uber-clone --ignore-not-found=true

echo -e "${GREEN}✓ All resources deleted${NC}"
echo ""

read -p "Do you want to stop Minikube? (yes/no): " -r
echo

if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Stopping Minikube...${NC}"
    minikube stop
    echo -e "${GREEN}✓ Minikube stopped${NC}"
fi

read -p "Do you want to delete Minikube cluster? (yes/no): " -r
echo

if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Deleting Minikube cluster...${NC}"
    minikube delete
    echo -e "${GREEN}✓ Minikube cluster deleted${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  Cleanup Complete!${NC}"
echo "=========================================="
