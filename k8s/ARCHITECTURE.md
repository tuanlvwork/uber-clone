# Kubernetes Architecture for Uber-Clone

## 📁 File Structure

```
uber-clone/
├── Dockerfile                          # Multi-service Python image
├── Dockerfile.frontend                 # Nginx frontend image
├── .dockerignore                       # Docker build exclusions
├── k8s/
│   ├── README.md                       # Detailed deployment guide
│   ├── QUICKSTART.md                   # Quick start guide
│   ├── nginx.conf                      # Nginx configuration
│   │
│   ├── 00-namespace.yaml               # uber-clone namespace
│   ├── 01-configmap.yaml               # Environment variables
│   ├── 02-secrets.yaml                 # Sensitive credentials
│   │
│   ├── 10-kafka.yaml                   # Kafka StatefulSet + Service
│   ├── 11-postgres.yaml                # PostgreSQL StatefulSet + Service
│   ├── 12-kafka-ui.yaml                # Kafka UI Deployment + NodePort
│   │
│   ├── 20-api-gateway.yaml             # API Gateway Deployment + Service
│   ├── 21-ride-service.yaml            # Ride Service Deployment + Service
│   ├── 22-driver-service.yaml          # Driver Service Deployment + Service
│   ├── 23-matching-service.yaml        # Matching Service Deployment + Service
│   ├── 24-location-service.yaml        # Location Service Deployment + Service
│   ├── 25-payment-service.yaml         # Payment Service Deployment + Service
│   │
│   ├── 30-frontend.yaml                # Frontend Deployment + NodePort
│   ├── 40-prometheus.yaml              # Prometheus Deployment + ConfigMap
│   ├── 41-grafana.yaml                 # Grafana Deployment + NodePort
│   │
│   └── scripts/
│       ├── deploy.sh                   # Automated deployment
│       ├── build.sh                    # Build Docker images
│       └── cleanup.sh                  # Remove all resources
```

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                       │
│                         (Minikube)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Namespace: uber-clone                                 │   │
│  │                                                        │   │
│  │  ┌──────────────────────────────────────────────────┐ │   │
│  │  │  Frontend Layer (NodePort: 30080)               │ │   │
│  │  │  ┌────────────────────────────────────────┐     │ │   │
│  │  │  │  Frontend (nginx) - 2 replicas         │     │ │   │
│  │  │  │  • Serves static HTML/CSS/JS           │     │ │   │
│  │  │  │  • Proxies API requests to Gateway     │     │ │   │
│  │  │  └────────────────────────────────────────┘     │ │   │
│  │  └──────────────────────────────────────────────────┘ │   │
│  │                                                        │   │
│  │  ┌──────────────────────────────────────────────────┐ │   │
│  │  │  Application Layer (ClusterIP)                  │ │   │
│  │  │                                                  │ │   │
│  │  │  ┌────────────────┐  ┌────────────────┐       │ │   │
│  │  │  │  API Gateway   │  │  Ride Service  │       │ │   │
│  │  │  │  (2 replicas)  │  │  (2 replicas)  │       │ │   │
│  │  │  │  Port: 8001    │  │  Port: 8002    │       │ │   │
│  │  │  └────────────────┘  └────────────────┘       │ │   │
│  │  │                                                  │ │   │
│  │  │  ┌────────────────┐  ┌────────────────┐       │ │   │
│  │  │  │ Driver Service │  │Matching Service│       │ │   │
│  │  │  │  (2 replicas)  │  │  (2 replicas)  │       │ │   │
│  │  │  │  Port: 8003    │  │  Port: 8004    │       │ │   │
│  │  │  └────────────────┘  └────────────────┘       │ │   │
│  │  │                                                  │ │   │
│  │  │  ┌────────────────┐  ┌────────────────┐       │ │   │
│  │  │  │Location Service│  │Payment Service │       │ │   │
│  │  │  │  (2 replicas)  │  │  (2 replicas)  │       │ │   │
│  │  │  │  Port: 8005    │  │  Port: 8006    │       │ │   │
│  │  │  └────────────────┘  └────────────────┘       │ │   │
│  │  └──────────────────────────────────────────────────┘ │   │
│  │                                                        │   │
│  │  ┌──────────────────────────────────────────────────┐ │   │
│  │  │  Data Layer (StatefulSets)                      │ │   │
│  │  │                                                  │ │   │
│  │  │  ┌──────────────────┐  ┌──────────────────┐   │ │   │
│  │  │  │  Kafka (KRaft)   │  │   PostgreSQL     │   │ │   │
│  │  │  │  1 replica       │  │   1 replica      │   │ │   │
│  │  │  │  9092, 29092     │  │   Port: 5432     │   │ │   │
│  │  │  │  PVC: 1Gi        │  │   PVC: 2Gi       │   │ │   │
│  │  │  └──────────────────┘  └──────────────────┘   │ │   │
│  │  └──────────────────────────────────────────────────┘ │   │
│  │                                                        │   │
│  │  ┌──────────────────────────────────────────────────┐ │   │
│  │  │  Monitoring Layer (NodePort)                    │ │   │
│  │  │                                                  │ │   │
│  │  │  ┌──────────────────┐  ┌──────────────────┐   │ │   │
│  │  │  │   Kafka UI       │  │   Prometheus     │   │ │   │
│  │  │  │   1 replica      │  │   1 replica      │   │ │   │
│  │  │  │   Port: 30090    │  │   Port: 30090    │   │ │   │
│  │  │  └──────────────────┘  └──────────────────┘   │ │   │
│  │  │                                                  │ │   │
│  │  │  ┌──────────────────┐                          │ │   │
│  │  │  │     Grafana      │                          │ │   │
│  │  │  │   1 replica      │                          │ │   │
│  │  │  │   Port: 30030    │                          │ │   │
│  │  │  └──────────────────┘                          │ │   │
│  │  └──────────────────────────────────────────────────┘ │   │
│  │                                                        │   │
│  │  ┌──────────────────────────────────────────────────┐ │   │
│  │  │  Configuration                                   │ │   │
│  │  │  • ConfigMap: uber-config (env vars)            │ │   │
│  │  │  • Secret: uber-secrets (credentials)           │ │   │
│  │  └──────────────────────────────────────────────────┘ │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Service Dependencies

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │
       ↓
┌──────────────┐     ┌─────────────┐
│ API Gateway  │────→│    Kafka    │
└──────┬───────┘     └─────────────┘
       │                    ↑
       ↓                    │
┌──────────────┐            │
│  PostgreSQL  │            │
└──────────────┘            │
                            │
    ┌───────────────────────┴───────────────────────┐
    │           │           │           │           │
    ↓           ↓           ↓           ↓           ↓
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│  Ride  │ │ Driver │ │Matching│ │Location│ │Payment │
│Service │ │Service │ │Service │ │Service │ │Service │
└────┬───┘ └────┬───┘ └────────┘ └────────┘ └────┬───┘
     │          │                                  │
     └──────────┴──────────────────────────────────┘
                        ↓
                ┌──────────────┐
                │  PostgreSQL  │
                └──────────────┘
```

## 📊 Resource Allocation

### Infrastructure

| Component | Replicas | CPU Request | CPU Limit | Memory Request | Memory Limit | Storage |
|-----------|----------|-------------|-----------|----------------|--------------|---------|
| Kafka | 1 | 500m | 1000m | 512Mi | 1Gi | 1Gi PVC |
| PostgreSQL | 1 | 250m | 500m | 256Mi | 512Mi | 2Gi PVC |
| Kafka UI | 1 | 100m | 250m | 128Mi | 256Mi | - |

### Microservices

| Component | Replicas | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|----------|-------------|-----------|----------------|--------------|
| API Gateway | 2 | 250m | 500m | 256Mi | 512Mi |
| Ride Service | 2 | 200m | 400m | 256Mi | 512Mi |
| Driver Service | 2 | 200m | 400m | 256Mi | 512Mi |
| Matching Service | 2 | 200m | 400m | 256Mi | 512Mi |
| Location Service | 2 | 200m | 400m | 256Mi | 512Mi |
| Payment Service | 2 | 200m | 400m | 256Mi | 512Mi |

### Frontend & Monitoring

| Component | Replicas | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|----------|-------------|-----------|----------------|--------------|
| Frontend | 2 | 100m | 200m | 64Mi | 128Mi |
| Prometheus | 1 | 250m | 500m | 512Mi | 1Gi |
| Grafana | 1 | 200m | 400m | 256Mi | 512Mi |

**Total Resources Required:**
- **CPU**: ~4.5 cores (minimum cluster size: 4 CPUs)
- **Memory**: ~8 GB (minimum cluster size: 8 GB RAM)
- **Storage**: 3 GB persistent volumes

## 🔐 Security Features

1. **Namespace Isolation**: All resources in dedicated `uber-clone` namespace
2. **Secrets Management**: Credentials stored in Kubernetes Secrets
3. **Network Policies**: (Ready to implement) Service-to-service restrictions
4. **Resource Limits**: Prevent resource exhaustion attacks
5. **Health Checks**: Readiness and liveness probes for all services
6. **Init Containers**: Ensure dependencies are ready before starting

## 🚀 Deployment Features

### High Availability
- **2 replicas** for all microservices and frontend
- **Rolling updates** with zero downtime
- **Health checks** ensure traffic only to healthy pods

### Auto-healing
- **Liveness probes** restart unhealthy containers
- **Readiness probes** remove unhealthy pods from service
- **StatefulSets** for stateful components (Kafka, PostgreSQL)

### Observability
- **Prometheus** scrapes metrics from all services
- **Grafana** provides visualization dashboards
- **Kafka UI** for message broker inspection
- **Centralized logging** via `kubectl logs`

### Scalability
- **Horizontal Pod Autoscaler** ready
- **Resource requests/limits** defined
- **Service discovery** via Kubernetes DNS
- **Load balancing** via ClusterIP services

## 📈 Scaling Guide

### Manual Scaling

```bash
# Scale a specific service
kubectl scale deployment api-gateway -n uber-clone --replicas=3

# Scale all microservices
for service in api-gateway ride-service driver-service matching-service location-service payment-service; do
  kubectl scale deployment $service -n uber-clone --replicas=3
done
```

### Auto-scaling (HPA)

```bash
# Enable metrics server
minikube addons enable metrics-server

# Create HPA for API Gateway
kubectl autoscale deployment api-gateway -n uber-clone \
  --cpu-percent=70 \
  --min=2 \
  --max=10

# Apply to all services
for service in ride-service driver-service matching-service location-service payment-service; do
  kubectl autoscale deployment $service -n uber-clone \
    --cpu-percent=75 \
    --min=2 \
    --max=5
done
```

## 🔍 Monitoring Endpoints

All services expose Prometheus metrics at:
- API Gateway: `http://api-gateway:8001/metrics`
- Ride Service: `http://ride-service:8002/metrics`
- Driver Service: `http://driver-service:8003/metrics`
- Matching Service: `http://matching-service:8004/metrics`
- Location Service: `http://location-service:8005/metrics`
- Payment Service: `http://payment-service:8006/metrics`

## 🎯 Production Readiness Checklist

- [x] Container health checks
- [x] Resource limits defined
- [x] Persistent storage for stateful services
- [x] Secrets for sensitive data
- [x] Service discovery via DNS
- [x] Monitoring and metrics
- [ ] Network policies for pod isolation
- [ ] TLS/SSL certificates
- [ ] Ingress controller for routing
- [ ] Backup and disaster recovery
- [ ] CI/CD pipeline
- [ ] Multi-node cluster

## 📝 Next Steps for Production

1. **Ingress Setup**: Replace NodePort with Ingress controller
2. **TLS Certificates**: Use cert-manager for HTTPS
3. **Persistent Volumes**: Configure proper PV/PVC with cloud storage
4. **Network Policies**: Implement pod-to-pod communication restrictions
5. **RBAC**: Set up role-based access control
6. **Backup Strategy**: Implement automated backups for Kafka and PostgreSQL
7. **CI/CD**: Automate builds and deployments with GitHub Actions
8. **Monitoring Alerts**: Configure Grafana alerts
9. **Log Aggregation**: Add ELK or Loki stack
10. **Multi-region**: Deploy across availability zones

## 🆘 Quick Commands

```bash
# Deploy everything
./k8s/scripts/deploy.sh

# Check status
kubectl get all -n uber-clone

# View logs
kubectl logs -f deployment/api-gateway -n uber-clone

# Port forward for debugging
kubectl port-forward -n uber-clone svc/api-gateway 8001:8001

# Restart a service
kubectl rollout restart deployment api-gateway -n uber-clone

# Delete everything
./k8s/scripts/cleanup.sh
```

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)
- [Kafka on Kubernetes](https://strimzi.io/)
