# Uber Clone with Kafka

A production-ready microservices-based Uber clone with Apache Kafka for real-time event streaming and **Kubernetes orchestration**.

## 🚀 Deployment Options

| Method | Environment | Command | Features |
|--------|-------------|---------|----------|
| **Kubernetes** ✅ | Production | `./k8s/scripts/deploy.sh` | High Availability, Auto-scaling, Self-healing |
| **Docker Compose** | Development | `./start.sh` | Quick setup, Local testing |

**→ See [k8s/QUICKSTART.md](k8s/QUICKSTART.md) for Kubernetes deployment**

## Architecture

This application consists of multiple microservices communicating via Kafka:

- **Ride Service**: Handles ride requests from customers
- **Driver Service**: Manages driver availability and location updates
- **Matching Service**: Matches riders with available drivers
- **Location Service**: Tracks and broadcasts real-time locations
- **Payment Service**: Processes payments and refunds
- **API Gateway**: FastAPI-based gateway for frontend communication
- **Frontend**: Modern web interface for riders and drivers
- **Monitoring Stack**: Prometheus for metrics collection and Grafana for visualization

📖 **For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md)**

## Kafka Topics

- `ride-requests`: New ride requests from customers
- `driver-locations`: Real-time driver location updates
- `driver-availability`: Driver online/offline status
- `ride-matches`: Successful rider-driver matches
- `ride-updates`: Ride status updates (accepted, started, completed)

## Prerequisites

### For Local Development (Docker Compose)
- Python 3.8+
- Docker & Docker Compose

### For Kubernetes Deployment (Production)
- Docker
- Minikube (`brew install minikube`)
- kubectl (`brew install kubectl`)
- 4 CPU cores, 8GB RAM minimum

### Optional
- Node.js (for frontend development)

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
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## Quick Start with Script

```bash
# Start all services at once
./start.sh
```

## Kubernetes Deployment

Deploy the entire application to Kubernetes using Minikube:

### 🚀 Quick Deploy (3 commands)

```bash
# 1. Run the deployment script
./k8s/scripts/deploy.sh

# 2. Wait for pods to be ready
kubectl get pods -n uber-clone -w

# 3. Access the app
minikube service frontend -n uber-clone
```

### 📚 Documentation

- **[Quick Start Guide](k8s/QUICKSTART.md)** - Get running in minutes
- **[Detailed Guide](k8s/README.md)** - Complete documentation with troubleshooting

### 🎯 What You Get

The Kubernetes deployment includes:
- ✅ **Infrastructure**: Kafka (KRaft), PostgreSQL, Kafka UI
- ✅ **Microservices**: All 6 services with 2 replicas each
- ✅ **Frontend**: Nginx-based static file server
- ✅ **Monitoring**: Prometheus + Grafana
- ✅ **Auto-scaling**: Ready for HPA configuration
- ✅ **Health Checks**: Readiness and liveness probes

### 🔗 Accessing Services

After deployment:
```bash
MINIKUBE_IP=$(minikube ip)
echo "Frontend:  http://$MINIKUBE_IP:30080"
echo "Kafka UI:  http://$MINIKUBE_IP:30090"
echo "Grafana:   http://$MINIKUBE_IP:30030"
```

### 🧹 Cleanup

```bash
./k8s/scripts/cleanup.sh
```

## Testing

```bash
# Run unit tests
pytest tests/

# Test Kafka connectivity
python scripts/test_kafka.py
```

## Monitoring

The application includes a comprehensive monitoring stack using Prometheus and Grafana.

### Accessing Dashboards

- **Grafana**: http://localhost:3000 (User: `admin`, Pass: `admin`)
- **Prometheus**: http://localhost:9090

### Metrics

All microservices are instrumented to expose:
- **System Metrics**: CPU, Memory, Garbage Collection
- **Application Metrics**: Request latency, error rates, request counts

For more details, see [MONITORING.md](MONITORING.md).

## Project Structure

```
uber-clone/
├── services/
│   ├── ride_service.py         # Handles ride requests
│   ├── driver_service.py       # Manages drivers
│   ├── matching_service.py     # Matches rides with drivers
│   ├── location_service.py     # Tracks locations
│   ├── payment_service.py      # Payment processing
│   └── api_gateway.py          # Main API endpoint
├── frontend/
│   ├── index.html             # Main landing page
│   ├── rider.html             # Rider interface
│   ├── driver.html            # Driver interface
│   ├── styles.css             # Styles
│   └── app.js                 # Frontend logic
├── k8s/                       # ✅ Kubernetes deployment files
│   ├── scripts/
│   │   ├── deploy.sh          # One-command deployment
│   │   ├── build.sh           # Build Docker images
│   │   └── cleanup.sh         # Remove all resources
│   ├── 00-namespace.yaml      # Kubernetes namespace
│   ├── 01-configmap.yaml      # Configuration
│   ├── 02-secrets.yaml        # Secrets
│   ├── 10-kafka.yaml          # Kafka StatefulSet
│   ├── 11-postgres.yaml       # PostgreSQL StatefulSet
│   ├── 12-kafka-ui.yaml       # Kafka UI
│   ├── 20-api-gateway.yaml    # API Gateway deployment
│   ├── 21-25-...-service.yaml # Microservices (x6)
│   ├── 30-frontend.yaml       # Frontend deployment
│   ├── 40-prometheus.yaml     # Prometheus monitoring
│   ├── 41-grafana.yaml        # Grafana dashboards
│   ├── QUICKSTART.md          # Quick deployment guide
│   ├── README.md              # Detailed K8s guide
│   ├── ARCHITECTURE.md        # K8s architecture
│   └── CHECKLIST.md           # Deployment checklist
├── models/
│   └── database.py            # Database models
├── scripts/
│   ├── init_db.py            # Database initialization
│   └── test_kafka.py         # Kafka testing
├── config/
│   └── prometheus.yml         # Prometheus configuration
├── Dockerfile                 # Microservices image
├── Dockerfile.frontend        # Frontend (nginx) image
├── .dockerignore             # Docker build optimization
├── docker-compose.yml         # Local development stack
├── requirements.txt           # Python dependencies
├── start.sh                  # Local startup script
├── stop.sh                   # Local shutdown script
├── README.md                 # This file
├── ARCHITECTURE.md           # Architecture documentation
├── MONITORING.md             # Monitoring guide
└── USER_GUIDE.md             # End-user guide
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

- [x] Payment integration
- [ ] Rating system
- [ ] Surge pricing
- [ ] Multi-vehicle types
- [ ] Chat between rider and driver
- [x] PostgreSQL database
- [ ] Redis caching
- [x] Kubernetes deployment
- [x] Monitoring with Prometheus/Grafana

## License

MIT License
