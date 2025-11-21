#!/bin/bash

# Uber Clone with Kafka - Start Script
# This script starts all services in the background

echo "=================================================="
echo "   Uber Clone with Kafka - Starting Services"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Kafka is running
echo ""
echo -e "${YELLOW}Checking Kafka status...${NC}"
if ! docker ps | grep -q uber-kafka; then
    echo -e "${YELLOW}Kafka is not running. Starting Docker containers...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✓ Waiting for Kafka to be ready (30 seconds)...${NC}"
    sleep 30
else
    echo -e "${GREEN}✓ Kafka is already running${NC}"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo ""
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Initialize database if it doesn't exist
if [ ! -f "uber.db" ]; then
    echo ""
    echo -e "${YELLOW}Initializing database...${NC}"
    python scripts/init_db.py
    echo -e "${GREEN}✓ Database initialized${NC}"
fi

# Create logs directory
mkdir -p logs

# Start services
echo ""
echo -e "${YELLOW}Starting microservices...${NC}"

echo -e "${GREEN}Starting Ride Service...${NC}"
nohup python services/ride_service.py > logs/ride_service.log 2>&1 &
RIDE_PID=$!
echo "  PID: $RIDE_PID"

sleep 2

echo -e "${GREEN}Starting Driver Service...${NC}"
nohup python services/driver_service.py > logs/driver_service.log 2>&1 &
DRIVER_PID=$!
echo "  PID: $DRIVER_PID"

sleep 2

echo -e "${GREEN}Starting Matching Service...${NC}"
nohup python services/matching_service.py > logs/matching_service.log 2>&1 &
MATCHING_PID=$!
echo "  PID: $MATCHING_PID"

sleep 2

echo -e "${GREEN}Starting Location Service...${NC}"
nohup python services/location_service.py > logs/location_service.log 2>&1 &
LOCATION_PID=$!
echo "  PID: $LOCATION_PID"

sleep 2

echo -e "${GREEN}Starting API Gateway...${NC}"
nohup python services/api_gateway.py > logs/api_gateway.log 2>&1 &
API_PID=$!
echo "  PID: $API_PID"

sleep 3

# Start Frontend Server
echo -e "${YELLOW}Starting Frontend Server...${NC}"
nohup python -m http.server 8080 --directory frontend > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
PIDS+=($FRONTEND_PID)
echo "  PID: $FRONTEND_PID"

# Save PIDs for cleanup
echo "$RIDE_PID,$DRIVER_PID,$MATCHING_PID,$LOCATION_PID,$API_PID,$FRONTEND_PID" > .service_pids

echo ""
echo "=================================================="
echo -e "${GREEN}   All Services Started Successfully!${NC}"
echo "=================================================="
echo ""
echo "Service URLs:"
echo "  • API Gateway:    http://localhost:8001"
echo "  • Rider App:      http://localhost:8080/rider.html"
echo "  • Driver App:     http://localhost:8080/driver.html"
echo "  • Kafka UI:       http://localhost:8090"
echo ""
echo "Logs are available in the logs/ directory"
echo ""
echo "To stop all services, run: ./stop.sh"
echo ""
echo "To view API documentation:"
echo "  open http://localhost:8001/docs"
echo ""
echo "=================================================="
