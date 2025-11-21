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
│                    Port 8000                                │
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
              │   SQLite    │
              │  Database   │
              └─────────────┘
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

### 2. **API Gateway** (Port 8000)
- **FastAPI** REST API
- Routes HTTP requests to services
- OpenAPI/Swagger documentation
- CORS enabled for frontend

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
- **Ride Service**
  - Creates ride requests
  - Updates ride status
  - Publishes to `ride-requests`
  
- **Driver Service**
  - Manages driver availability
  - Updates location
  - Handles ride actions (accept/start/complete)
  
- **Matching Service**
  - Finds nearest driver (Haversine algorithm)
  - Calculates fares
  - Publishes to `ride-matches`
  
- **Location Service**
  - Tracks driver locations
  - Broadcasts to riders
  - Manages availability

### 5. **Data Layer**
- **SQLite Database**
  - Riders table
  - Drivers table
  - Rides table (with status tracking)

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
| Database | SQLite | Data persistence |
| Container | Docker | Kafka/Zookeeper |

---

## Ports Summary

- **8000** - API Gateway
- **8080** - Frontend (optional http-server)
- **8090** - Kafka UI Dashboard
- **9093** - Kafka Broker (external)
- **2181** - Zookeeper

---

*This is a simplified architecture suitable for learning and development.*
*For production, consider adding: authentication, load balancers, monitoring, logging, and distributed databases.*
