# Uber Clone with Kafka

A microservices-based Uber clone application demonstrating Apache Kafka for real-time event streaming.

## Architecture

This application consists of multiple microservices communicating via Kafka:

- **Ride Service**: Handles ride requests from customers
- **Driver Service**: Manages driver availability and location updates
- **Matching Service**: Matches riders with available drivers
- **Location Service**: Tracks and broadcasts real-time locations
- **API Gateway**: FastAPI-based gateway for frontend communication
- **Frontend**: Modern web interface for riders and drivers

## Kafka Topics

- `ride-requests`: New ride requests from customers
- `driver-locations`: Real-time driver location updates
- `driver-availability`: Driver online/offline status
- `ride-matches`: Successful rider-driver matches
- `ride-updates`: Ride status updates (accepted, started, completed)

## Prerequisites

- Python 3.8+
- Docker & Docker Compose (for Kafka and Zookeeper)
- Node.js (optional, for frontend development)

## Installation

1. **Clone the repository**
```bash
cd /Users/tuanlv/Desktop/learn-space/kafka/gits/uber-clone
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Start Kafka and Zookeeper**
```bash
docker-compose up -d
```

5. **Initialize the database**
```bash
python scripts/init_db.py
```

## Running the Application

1. **Start all services** (in separate terminals):

```bash
# Terminal 1: Ride Service
python services/ride_service.py

# Terminal 2: Driver Service
python services/driver_service.py

# Terminal 3: Matching Service
python services/matching_service.py

# Terminal 4: Location Service
python services/location_service.py

# Terminal 5: API Gateway
python services/api_gateway.py
```

2. **Open the frontend**
```bash
# Open in browser
open frontend/index.html
# Or use a local server
python -m http.server 8080 --directory frontend
```

3. **Access the application**
- Rider Interface: http://localhost:8000/rider
- Driver Interface: http://localhost:8000/driver
- Admin Dashboard: http://localhost:8000/admin

## Quick Start with Script

```bash
# Start all services at once
./start.sh
```

## Testing

```bash
# Run unit tests
pytest tests/

# Test Kafka connectivity
python scripts/test_kafka.py
```

## Project Structure

```
uber-clone/
├── services/
│   ├── ride_service.py         # Handles ride requests
│   ├── driver_service.py       # Manages drivers
│   ├── matching_service.py     # Matches rides with drivers
│   ├── location_service.py     # Tracks locations
│   └── api_gateway.py          # Main API endpoint
├── frontend/
│   ├── index.html             # Main landing page
│   ├── rider.html             # Rider interface
│   ├── driver.html            # Driver interface
│   ├── styles.css             # Styles
│   └── app.js                 # Frontend logic
├── kafka/
│   └── kafka_config.py        # Kafka configuration
├── models/
│   └── database.py            # Database models
├── scripts/
│   ├── init_db.py            # Database initialization
│   └── test_kafka.py         # Kafka testing
├── docker-compose.yml         # Kafka & Zookeeper setup
├── requirements.txt           # Python dependencies
└── README.md
```

## Features

### Rider Features
- Request rides with pickup and destination
- Real-time driver tracking
- Ride status updates
- Fare estimation
- Ride history

### Driver Features
- Toggle online/offline status
- Accept/reject ride requests
- Navigate to pickup location
- Update ride status
- Earnings tracking

### System Features
- Real-time location tracking
- Intelligent driver matching (based on proximity)
- Event-driven architecture with Kafka
- Scalable microservices design
- WebSocket for real-time updates

## Kafka Event Flow

1. **Ride Request Flow**:
   - Rider requests ride → `ride-requests` topic
   - Matching service consumes request
   - Finds nearest available driver
   - Publishes match → `ride-matches` topic

2. **Location Update Flow**:
   - Driver sends location → `driver-locations` topic
   - Location service broadcasts to relevant riders
   - Real-time map updates

3. **Ride Status Flow**:
   - Driver accepts/starts/completes ride
   - Publishes status → `ride-updates` topic
   - Rider receives real-time notifications

## Configuration

Edit `kafka/kafka_config.py` to customize:
- Kafka broker addresses
- Topic configurations
- Consumer group IDs
- Retry policies

## Troubleshooting

**Kafka Connection Issues**:
```bash
# Check if Kafka is running
docker-compose ps

# View Kafka logs
docker-compose logs kafka

# Restart Kafka
docker-compose restart
```

**Database Issues**:
```bash
# Reset database
rm uber.db
python scripts/init_db.py
```

## Future Enhancements

- [ ] Payment integration
- [ ] Rating system
- [ ] Surge pricing
- [ ] Multi-vehicle types
- [ ] Chat between rider and driver
- [ ] PostgreSQL database
- [ ] Redis caching
- [ ] Kubernetes deployment
- [ ] Monitoring with Prometheus/Grafana

## License

MIT License
