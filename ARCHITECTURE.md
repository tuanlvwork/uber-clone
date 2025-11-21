# Uber Clone - Simple Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                           │
├─────────────────────────┬───────────────────────────────────┤
│     Rider App 👤        │      Driver App 🚗               │
│   (Request Rides)       │    (Accept Rides)                 │
└──────────┬──────────────┴───────────────┬───────────────────┘
           │                               │
           └───────────────┬───────────────┘
                           │ HTTP/REST
                    ┌──────▼──────┐
                    │             │
┌───────────────────┴─────────────┴───────────────────────────┐
│               API GATEWAY (FastAPI)                         │
│                    Port 8001                                │
└──────────────────────────┬──────────────────────────────────┘
                           │ Publish/Subscribe Events
                    ┌──────▼──────┐
┌───────────────────┴─────────────┴───────────────────────────┐
│                  APACHE KAFKA                               │
│                 Message Broker                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Topics:                                           │   │
│  │  • ride-requests      • driver-locations          │   │
│  │  • ride-matches       • ride-updates              │   │
│  │  • driver-availability                             │   │
│  └────────────────────────────────────────────────────┘   │
└──────┬─────────┬──────────┬──────────┬─────────────────────┘
       │         │          │          │
   ┌───▼───┐ ┌──▼───┐  ┌──▼────┐ ┌───▼──────┐
   │ Ride  │ │Driver│  │Matching│ │Location  │
   │Service│ │Service│  │Service │ │Service   │
   └───┬───┘ └──┬───┘  └──┬────┘ └───┬──────┘
       │        │         │           │
       └────────┴─────────┴───────────┘
                     │
              ┌──────▼──────┐
              │  PostgreSQL │
              │  Database   │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │  Monitoring │
              │    Stack    │
              └─────────────┘
       (Prometheus & Grafana)
```

## Architecture Components

### 1. **Client Layer**
- **Rider App** (frontend/rider.html)
  - Request rides
  - Track driver location
  - View ride history
  
- **Driver App** (frontend/driver.html)
  - Toggle online/offline
  - Accept ride requests
  - Update location
  - Complete rides

### 2. **API Gateway** (Port 8001)
- **FastAPI** REST API
- Routes HTTP requests to services
- OpenAPI/Swagger documentation
- CORS enabled for frontend
- Prometheus metrics exposed at `/metrics`

### 3. **Apache Kafka** (Port 9093)
Event-driven message broker with 5 topics:

| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| `ride-requests` | Ride Service | Matching Service | New ride requests |
| `driver-locations` | Driver Service | Location Service | Real-time GPS updates |
| `driver-availability` | Driver Service | Location Service | Online/offline status |
| `ride-matches` | Matching Service | Ride Service | Matched rides |
| `ride-updates` | Driver Service | Ride Service | Status changes |

### 4. **Microservices**
- **Ride Service** (Port 8002)
  - Creates ride requests
  - Updates ride status
  - Publishes to `ride-requests`
  - Exposes Prometheus metrics
  
- **Driver Service** (Port 8003)
  - Manages driver availability
  - Updates location
  - Handles ride actions (accept/start/complete)
  - Exposes Prometheus metrics
  
- **Matching Service** (Port 8004)
  - Finds nearest driver (Haversine algorithm)
  - Calculates fares
  - Publishes to `ride-matches`
  - Exposes Prometheus metrics
  
- **Location Service** (Port 8005)
  - Tracks driver locations
  - Broadcasts to riders
  - Manages availability
  - Exposes Prometheus metrics

### 5. **Data Layer**
- **PostgreSQL Database** (Port 5432)
  - Riders table
  - Drivers table
  - Rides table (with status tracking)
  - Payments table

### 6. **Monitoring Stack**
- **Prometheus** (Port 9090)
  - Metrics collection from all services
  - Time-series database
  - Query interface for metrics
  
- **Grafana** (Port 3000)
  - Visualization dashboards
  - Real-time monitoring
  - Alerting capabilities

---

## Data Flow Example: Requesting a Ride

```
1. Rider App → API Gateway
   POST /api/rides (pickup, destination, vehicle type)

2. API Gateway → Ride Service
   Create ride in database

3. Ride Service → Kafka
   Publish to 'ride-requests' topic

4. Kafka → Matching Service
   Consume ride request

5. Matching Service
   Query database for available drivers
   Calculate nearest driver (Haversine)
   Calculate fare

6. Matching Service → Kafka
   Publish to 'ride-matches' topic

7. Kafka → Ride Service
   Consume match, update ride status

8. Ride Service → Database
   Update ride with driver_id, fare

9. Rider App polls API Gateway
   GET /api/rides/{id}
   Sees matched status with driver info
```

---

## Key Patterns

### Event-Driven Architecture
- Services communicate via Kafka events
- Loose coupling between services
- Async processing
- Scalability through partitioning

### Microservices
- Independent deployment
- Single responsibility
- Technology flexibility
- Fault isolation

### Real-Time Updates
- Kafka streaming
- Location broadcasting
- Status notifications
- Sub-second latency

---

## Scalability

Current: **Single Instance**
- 1 Kafka broker
- 1 database
- Services run on single machine

Future: **Distributed**
- Kafka cluster (3+ brokers)
- PostgreSQL with replicas
- Redis for caching
- Load-balanced API gateways
- Kubernetes orchestration

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | HTML/CSS/JS | User interface |
| API | FastAPI | REST endpoints |
| Messaging | Apache Kafka | Event streaming |
| Services | Python | Business logic |
| Database | PostgreSQL | Data persistence |
| Container | Docker | Kafka/PostgreSQL/Monitoring |
| Monitoring | Prometheus | Metrics collection |
| Visualization | Grafana | Dashboards & alerts |

---

## Ports Summary

**Frontend & API:**
- **8001** - API Gateway
- **8080** - Frontend (http-server)

**Microservices Metrics:**
- **8002** - Ride Service (Prometheus metrics)
- **8003** - Driver Service (Prometheus metrics)
- **8004** - Matching Service (Prometheus metrics)
- **8005** - Location Service (Prometheus metrics)

**Infrastructure:**
- **9093** - Kafka Broker (external)
- **29092** - Kafka Broker (internal)
- **5432** - PostgreSQL Database

**Monitoring & Management:**
- **3000** - Grafana Dashboard
- **9090** - Prometheus
- **8090** - Kafka UI Dashboard

---

*This architecture demonstrates a production-ready microservices system with event-driven communication, distributed database, and comprehensive monitoring.*

**Implemented Features:**
- ✅ Event-driven architecture with Kafka
- ✅ PostgreSQL database with proper schema
- ✅ Prometheus & Grafana monitoring
- ✅ Payment service integration
- ✅ Real-time location tracking

**Future Enhancements:**
- Authentication & authorization
- Load balancers for high availability
- Distributed tracing (Jaeger/Zipkin)
- Redis caching layer
- Kubernetes orchestration

