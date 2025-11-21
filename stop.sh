#!/bin/bash

# Uber Clone with Kafka - Stop Script
# This script stops all running services

echo "=================================================="
echo "   Stopping All Services"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Read PIDs from file
# Stop Python services by pattern and port
echo "Stopping Python services..."

# Kill API Gateway on port 8001
API_PID=$(lsof -ti:8001)
if [ ! -z "$API_PID" ]; then
    echo "  Stopping API Gateway (PID: $API_PID)"
    kill -9 $API_PID
fi

# Kill Frontend Server on port 8080
FRONTEND_PID=$(lsof -ti:8080)
if [ ! -z "$FRONTEND_PID" ]; then
    echo "  Stopping Frontend Server (PID: $FRONTEND_PID)"
    kill -9 $FRONTEND_PID
fi

# Kill any remaining python services
pkill -f "python services/"
pkill -f "python -m http.server"

rm -f .service_pids
echo -e "${GREEN}✓ Python services stopped${NC}"

# Stop Docker containers
echo ""
echo "Stopping Docker containers..."
docker-compose down
echo -e "${GREEN}✓ Docker containers stopped${NC}"

echo ""
echo "=================================================="
echo -e "${GREEN}   All Services Stopped${NC}"
echo "=================================================="
