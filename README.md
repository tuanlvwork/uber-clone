# Uber Clone with Apache Kafka

A production-ready, event-driven microservices application demonstrating real-time ride-sharing with Apache Kafka, Kubernetes, and WebSocket support.

[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?logo=kubernetes)](k8s/README.md)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](docker-compose.yml)
[![Kafka](https://img.shields.io/badge/Apache-Kafka-231F20?logo=apache-kafka)](https://kafka.apache.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql)](https://www.postgresql.org/)

## 🚀 Quick Start

### Kubernetes Deployment (Recommended)

One command to deploy the entire stack:

```bash
./k8s/scripts/deploy.sh
```

Access at: `http://$(minikube ip)/`

**[→ Full Kubernetes Guide](k8s/README.md)**

### Docker Compose (Development)

```bash
./start.sh
```

Access at: `http://localhost:8080`

---

## 📊 Architecture

### System Overview

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
   ┌───▼────┐
   │Ingress │ (Kubernetes) / Nginx (Docker Compose)
   └───┬────┘
       │
   ┌───▼────────────┐
   │  API Gateway   │ (FastAPI + WebSocket)
   └────┬───────────┘
        │
   ┌────▼─────┐
   │  Kafka   │ (Message Broker - KRaft Mode)
   └────┬─────┘
        │
   ┌────▼──────────────────────────────────┐
   │ Microservices (Producers/Consumers)   │
   ├───────────┬────────────┬──────────────┤
   │   Ride    │   Driver   │   Matching   │
   │  Service  │  Service   │   Service    │
   └───────────┴────────────┴──────────────┘
        │                                    
   ┌────▼──────┐
   │PostgreSQL │ (Database)
   └───────────┘
```

### Microservices

- **Ride Service**: Manages ride lifecycle (request → matched → started → completed)
- **Driver Service**: Handles driver availability and accepts rides
- **Matching Service**: Intelligently matches riders with nearby drivers
- **Location Service**: Tracks real-time GPS locations via Kafka streams
- **API Gateway**: Unified REST + WebSocket interface for frontend
- **Frontend**: Modern SPA with real-time updates

### Kafka Topics

| Topic | Purpose | Producer | Consumer |
|-------|---------|----------|----------|
| `ride-requests` | New ride requests | API Gateway | Matching Service |
| `driver-locations` | GPS updates | API Gateway | Location Service, API Gateway |
| `driver-availability` | Online/offline status | API Gateway | Location Service |
| `ride-matches` | Successful matches | Matching Service | Ride Service |
| `ride-updates` | Status changes | Driver Service | API Gateway, Ride Service |

## 🔧 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Vanilla JS + Leaflet.js | Interactive maps, real-time tracking |
| **API** | FastAPI + WebSockets | REST + real-time communication |
| **Services** | Python 3.9 | Microservices implementation |
| **Messaging** | Apache Kafka (KRaft) | Event streaming & service decoupling |
| **Database** | PostgreSQL 13 | Persistent data storage |
| **Monitoring** | Prometheus + Grafana | Metrics & visualization |
| **Orchestration** | Kubernetes + Docker Compose | Deployment & scaling |
| **Proxy** | Nginx + Ingress | Load balancing & routing |

## 📦 Deployment Options

### 🎯 Kubernetes (Production)

**Best for:** Production, staging, CI/CD pipelines

```bash
# One-command deployment
./k8s/scripts/deploy.sh

# Access via Ingress
http://$(minikube ip)/            # Frontend
http://$(minikube ip)/api/        # API Gateway
http://$(minikube ip)/kafka-ui/   # Kafka UI
http://$(minikube ip)/grafana/    # Grafana
```

**Features:**
- ✅ Auto-scaling with HPA
- ✅ Self-healing pods
- ✅ Rolling updates
- ✅ Resource management
- ✅ Ingress routing
- ✅ Health checks

**[→ Kubernetes Guide](k8s/README.md)**

### 🐳 Docker Compose (Development)

**Best for:** Local development, quick testing

```bash
# Start all services
./start.sh

# Access
http://localhost:8080       # Frontend
http://localhost:8001       # API Gateway
http://localhost:9090       # Prometheus
http://localhost:3000       # Grafana
```

**Features:**
- ✅ Single command setup
- ✅ Hot reload support
- ✅ Easy debugging
- ✅ Volume mounts for development

## 🌐 Application Features

### For Riders
- 🗺️ **Interactive Map**: Visual ride booking with pickup/destination selection
- 📍 **Real-Time Tracking**: Live driver location updates via WebSocket
- 📊 **Ride History**: View past rides with detailed information
- 💳 **Payment Processing**: Secure payment handling

### For Drivers
- 🚗 **Availability Toggle**: Go online/offline instantly
- 📍 **Location Updates**: Automatic GPS broadcasting every 10 seconds
- 🔔 **Ride Notifications**: Real-time ride requests
- 💰 **Earnings Tracking**: View completed rides and total earnings

### For Admins
- 📊 **Live Dashboard**: Monitor all active drivers on a map
- 📈 **Metrics**: Prometheus metrics with Grafana dashboards
- 🔍 **Kafka UI**: Inspect topics, messages, and consumer groups
- 📝 **Logs**: Centralized logging for all services

## 📋 Prerequisites

### Required
- **Docker** 20.10+
- **Docker Compose** 2.0+ (for local dev)
- **Minikube** 1.33+ (for Kubernetes)
- **kubectl** 1.27+ (for Kubernetes)

### System Requirements
- **For Docker Compose**: 4GB RAM, 2 CPU cores
- **For Kubernetes**: 8GB RAM, 4 CPU cores (recommended)

### Install on macOS
```bash
brew install docker docker-compose minikube kubectl
```

## 🚀 Getting Started

### Option 1: Kubernetes (Production-like)

```bash
# 1. Clone repository
git clone <repo-url>
cd uber-clone

# 2. Deploy to Kubernetes
./k8s/scripts/deploy.sh

# 3. Access application
open "http://$(minikube ip)/"
```

### Option 2: Docker Compose (Quick Start)

```bash
# 1. Clone repository
git clone <repo-url>
cd uber-clone

# 2. Start services
./start.sh

# 3. Access application
open http://localhost:8080
```

## 📖 Documentation

- **[Architecture Guide](ARCHITECTURE.md)**: Detailed system architecture
- **[Kubernetes Deployment](k8s/README.md)**: K8s deployment guide
- **[User Guide](USER_GUIDE.md)**: How to use the application
- **[Monitoring Guide](MONITORING.md)**: Prometheus & Grafana setup

## 🔍 Monitoring & Observability

### Prometheus Metrics

All services expose metrics at `/metrics`:
- Request counts & latencies
- Kafka message throughput
- Database connection pool stats
- Custom business metrics

### Grafana Dashboards

Pre-configured dashboards for:
- Service health overview
- Kafka topic monitoring  
- Database performance
- Request/response metrics

**Access Grafana:**
- Kubernetes: `http://$(minikube ip)/grafana/`
- Docker Compose: `http://localhost:3000`
- Credentials: `admin / admin`

### Kafka UI

Monitor topics, consumers, and messages:
- Kubernetes: `http://$(minikube ip)/kafka-ui/`
- Docker Compose: `http://localhost:8080/kafka-ui/`

## 🧪 Testing

### Manual Testing

1. **Open Rider App**: http://localhost:8080/rider.html
2. **Create a ride request** with pickup/destination
3. **Open Driver App**: http://localhost:8080/driver.html
4. **Go online** and accept the ride
5. **Track in real-time**: http://localhost:8080/tracking.html

### API Testing

```bash
# Health check
curl http://localhost:8001/health

# List riders
curl http://localhost:8001/api/riders/1

# Get nearby drivers
curl "http://localhost:8001/api/drivers/nearby?lat=40.7128&lon=-74.0060"
```

## 🐛 Troubleshooting

### Kubernetes Issues

```bash
# Check pod status
kubectl get pods -n uber-clone

# View logs
kubectl logs -f deployment/api-gateway -n uber-clone

# Extract all logs to files
./k8s/scripts/extract_logs.sh
```

### Docker Compose Issues

```bash
# View logs
docker-compose logs -f api-gateway

# Restart a service
docker-compose restart ride-service

# Rebuild images
docker-compose build --no-cache
```

### Common Issues

| Problem | Solution |
|---------|----------|
| Pods pending | Reduce replicas or increase Minikube resources |
| Kafka connection failed | Wait for Kafka pod to be Running (takes ~60s) |
| Frontend shows errors | Check API Gateway logs for issues |
| WebSocket not connecting | Verify Ingress/proxy configuration |

## 🧹 Cleanup

### Kubernetes
```bash
./k8s/scripts/cleanup.sh
# or
kubectl delete namespace uber-clone
minikube delete
```

### Docker Compose
```bash
docker-compose down -v
```

## 📚 Project Structure

```
uber-clone/
├── services/              # Microservices
│   ├── api_gateway.py
│   ├── ride_service.py
│   ├── driver_service.py
│   ├── matching_service.py
│   └── location_service.py
├── frontend/              # Web UI
│   ├── index.html
│   ├── rider.html
│   ├── driver.html
│   └── tracking.html
├── k8s/                   # Kubernetes manifests
│   ├── scripts/           # Deployment scripts
│   ├── *.yaml            # K8s resources
│   └── README.md         # K8s guide
├── models/                # Database models
├── config/                # Configuration
├── docker-compose.yml     # Docker Compose config
└── start.sh              # Quick start script
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Apache Kafka for event streaming
- FastAPI for the excellent async framework
- Kubernetes community for orchestration tools
- Leaflet.js for interactive maps

---

**Made with ❤️ demonstrating event-driven microservices architecture**
