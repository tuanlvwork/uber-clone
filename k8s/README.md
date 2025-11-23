# Kubernetes Deployment Guide for Uber-Clone

This guide provides complete instructions for deploying the Uber-Clone application on Kubernetes using Minikube.

## 📋 Prerequisites

- **Docker** (for building images)
- **Minikube** v1.33+
- **kubectl** CLI
- **Homebrew** (macOS)

### Install Prerequisites

```bash
# Install Minikube and kubectl
brew install minikube kubectl

# Verify installations
minikube version
kubectl version --client
```

## 🚀 Quick Start (Automated)

### One-Command Deployment

The easiest way to deploy the entire application:

```bash
# Run the automated deployment script
./k8s/scripts/deploy.sh
```

This script will:
1. ✅ Start Minikube (if not running)
2. ✅ Build Docker images
3. ✅ Deploy all services (Kafka, PostgreSQL, microservices, frontend)
4. ✅ Set up Ingress for clean URLs
5. ✅ Deploy monitoring stack (Prometheus & Grafana)
6. ✅ Wait for all pods to be ready

**Access the application:**
- **Frontend**: `http://$(minikube ip)/`
- **With custom domain**: `http://uber-clone.local/` (after adding to /etc/hosts)

---

## 📘 Manual Deployment (Step-by-Step)

### 1. Start Minikube

```bash
# Start with sufficient resources (recommended for full stack)
minikube start --cpus=2 --memory=4096 --disk-size=20g --kubernetes-version=v1.30.0

# Verify cluster is running
kubectl cluster-info
```

### 2. Build Docker Images

```bash
# Point Docker to Minikube's daemon
eval $(minikube docker-env)

# Build the microservices image
docker build -t uber-clone:latest -f Dockerfile .

# Build the frontend image
docker build -t uber-clone-frontend:latest -f Dockerfile.frontend .

# Verify images
docker images | grep uber-clone
```

### 3. Deploy Infrastructure

```bash
# Create namespace
kubectl apply -f k8s/00-namespace.yaml

# Apply configuration
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secrets.yaml

# Deploy Kafka and PostgreSQL
kubectl apply -f k8s/10-kafka.yaml
kubectl apply -f k8s/11-postgres.yaml
kubectl apply -f k8s/12-kafka-ui.yaml

# Wait for infrastructure to be ready
kubectl wait --for=condition=ready pod -l app=kafka -n uber-clone --timeout=120s
kubectl wait --for=condition=ready pod -l app=postgres -n uber-clone --timeout=120s
```

### 4. Deploy Microservices

```bash
kubectl apply -f k8s/20-api-gateway.yaml
kubectl apply -f k8s/21-ride-service.yaml
kubectl apply -f k8s/22-driver-service.yaml
kubectl apply -f k8s/23-matching-service.yaml
kubectl apply -f k8s/24-location-service.yaml
```

### 5. Deploy Frontend

```bash
kubectl apply -f k8s/30-frontend.yaml
```

### 6. Deploy Monitoring (Optional)

```bash
kubectl apply -f k8s/40-prometheus.yaml
kubectl apply -f k8s/41-grafana.yaml
```

### 7. Set Up Ingress

```bash
# Enable Ingress addon
minikube addons enable ingress

# Apply Ingress configuration
kubectl apply -f k8s/50-ingress.yaml

# Wait for Ingress controller
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### 8. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n uber-clone

# Check Ingress
kubectl get ingress -n uber-clone

# Check services
kubectl get svc -n uber-clone
```

## 🌐 Accessing the Application

### Method 1: Ingress (Recommended)

Direct access via Minikube IP:
```bash
MINIKUBE_IP=$(minikube ip)
echo "Frontend: http://$MINIKUBE_IP/"
echo "API: http://$MINIKUBE_IP/api/"
echo "Kafka UI: http://$MINIKUBE_IP/kafka-ui/"
echo "Grafana: http://$MINIKUBE_IP/grafana/"
```

With custom domain (optional):
```bash
# Add to /etc/hosts
echo "$(minikube ip) uber-clone.local" | sudo tee -a /etc/hosts

# Access at clean URL
open http://uber-clone.local/
```

### Method 2: NodePort (Alternative)

```bash
MINIKUBE_IP=$(minikube ip)

# Frontend
open "http://$MINIKUBE_IP:30080"

# API Gateway
open "http://$MINIKUBE_IP:30001"

# Kafka UI
open "http://$MINIKUBE_IP:30090"

# Grafana
open "http://$MINIKUBE_IP:30030"
```

### Method 3: Minikube Service (For tunneling on macOS)

```bash
# Open frontend (creates tunnel automatically)
minikube service frontend -n uber-clone

# List all services
minikube service list -n uber-clone
```

## 📊 Architecture Overview

### Infrastructure Layer
- **Kafka** (StatefulSet): Message broker with KRaft mode (no ZooKeeper)
- **PostgreSQL** (StatefulSet): Relational database with persistent storage
- **Kafka UI**: Web interface for Kafka management

### Application Layer (1 replica each)
- **API Gateway**: FastAPI REST + WebSocket server
- **Ride Service**: Manages ride lifecycle
- **Driver Service**: Manages driver availability  
- **Matching Service**: Matches riders with drivers
- **Location Service**: Tracks real-time location

### Frontend Layer
- **Frontend** (Nginx): Serves static files with API proxy

### Monitoring Layer
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization and dashboards

### Routing Layer
- **Ingress**: Path-based routing for all services

## 🔍 Monitoring and Debugging

### View Logs

```bash
# View logs for a specific service
kubectl logs -f deployment/api-gateway -n uber-clone

# View logs for all pods of a service
kubectl logs -f -l app=ride-service -n uber-clone

# Extract all logs to files
./k8s/scripts/extract_logs.sh
# Logs saved to k8s/logs/
```

### Check Pod Status

```bash
# Get all pods with details
kubectl get pods -n uber-clone -o wide

# Watch pods in real-time
kubectl get pods -n uber-clone -w

# Describe a pod for detailed info
kubectl describe pod <pod-name> -n uber-clone
```

### Port Forwarding

```bash
# Forward API Gateway to localhost
kubectl port-forward -n uber-clone svc/api-gateway 8001:8001

# Forward PostgreSQL
kubectl port-forward -n uber-clone svc/postgres 5432:5432

# Forward Kafka
kubectl port-forward -n uber-clone svc/kafka 29092:29092
```

### Execute Commands in Pods

```bash
# Get a shell in a pod
kubectl exec -it deployment/api-gateway -n uber-clone -- /bin/bash

# Check Kafka topics
kubectl exec -it kafka-0 -n uber-clone -- \
  kafka-topics --bootstrap-server localhost:29092 --list

# Query PostgreSQL
kubectl exec -it postgres-0 -n uber-clone -- \
  psql -U uber -d uberdb -c "SELECT * FROM riders LIMIT 5;"
```

## 🔧 Configuration

### Environment Variables

Edit `k8s/01-configmap.yaml` to modify:
```yaml
KAFKA_BOOTSTRAP_SERVERS: "kafka:29092"
DATABASE_URL: "postgresql://uber:uberpassword@postgres:5432/uberdb"
```

### Secrets

Edit `k8s/02-secrets.yaml` for sensitive data:
```yaml
POSTGRES_PASSWORD: dWJlcnBhc3N3b3Jk  # base64 encoded
GRAFANA_ADMIN_PASSWORD: YWRtaW4=   # base64 encoded
```

After changes:
```bash
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secrets.yaml

# Restart deployments to pick up changes
kubectl rollout restart deployment -n uber-clone
```

## 📈 Scaling

### Manual Scaling

```bash
# Scale API Gateway to 2 replicas
kubectl scale deployment api-gateway -n uber-clone --replicas=2

# Scale all microservices
for service in api-gateway ride-service driver-service matching-service location-service; do
  kubectl scale deployment $service -n uber-clone --replicas=2
done
```

### Autoscaling (HPA)

```bash
# Enable metrics server
minikube addons enable metrics-server

# Create HPA for API Gateway
kubectl autoscale deployment api-gateway -n uber-clone \
  --cpu-percent=70 --min=1 --max=3

# View HPA status
kubectl get hpa -n uber-clone
```

## 🧹 Cleanup

### Using Cleanup Script

```bash
# Remove all resources
./k8s/scripts/cleanup.sh
```

### Manual Cleanup

```bash
# Delete the entire namespace
kubectl delete namespace uber-clone

# Delete Ingress controller
minikube addons disable ingress

# Stop Minikube
minikube stop

# Delete cluster (removes all data)
minikube delete
```

## 🐛 Troubleshooting

### Pods stuck in `Pending`

```bash
# Check pod events
kubectl describe pod <pod-name> -n uber-clone

# Common causes:
# - Insufficient resources → Reduce replicas or increase Minikube resources
# - PVC not bound → Check persistent volumes
```

**Solution:**
```bash
# Reduce replicas for all services
kubectl scale deployment --all -n uber-clone --replicas=1

# Or increase Minikube resources
minikube stop
minikube start --cpus=4 --memory=8192
```

### Pods stuck in `CrashLoopBackOff`

```bash
# View logs (current and previous)
kubectl logs <pod-name> -n uber-clone
kubectl logs <pod-name> -n uber-clone --previous

# Check all logs at once
./k8s/scripts/extract_logs.sh

# Common causes:
# - Kafka not ready → Wait for Kafka to be Running
# - Database connection → Check PostgreSQL is ready
# - Configuration error → Check ConfigMap
```

### Image pull errors

```bash
# Rebuild images in Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t uber-clone:latest -f Dockerfile .
docker build -t uber-clone-frontend:latest -f Dockerfile.frontend .

# Verify imagePullPolicy is set to IfNotPresent
kubectl get deployment api-gateway -n uber-clone -o yaml | grep imagePullPolicy
```

### Kafka connection issues

```bash
# Verify Kafka is running
kubectl get pods -l app=kafka -n uber-clone

# Check Kafka logs
kubectl logs kafka-0 -n uber-clone

# Test Kafka connectivity
kubectl exec deployment/api-gateway -n uber-clone -- \
  nc -zv kafka 29092
```

### Ingress not working

```bash
# Check Ingress status
kubectl get ingress -n uber-clone
kubectl describe ingress uber-clone-ingress -n uber-clone

# Verify Ingress controller is running
kubectl get pods -n ingress-nginx

# Restart Ingress controller
minikube addons disable ingress
minikube addons enable ingress
```

## 📚 Useful Scripts

All scripts are located in `k8s/scripts/`:

- **`deploy.sh`**: Complete automated deployment
- **`build.sh`**: Build only Docker images
- **`cleanup.sh`**: Remove all resources
- **`extract_logs.sh`**: Save all pod logs to files
- **`setup-ingress.sh`**: Configure Ingress (run separately if needed)
- **`start-tunnel.sh`**: Alternative access via minikube tunnel

## 🎯 Production Considerations

### Security
- [ ] Use external secret management (e.g., Vault)
- [ ] Implement Network Policies
- [ ] Enable RBAC
- [ ] Add Pod Security Policies
- [ ] Scan images for vulnerabilities

### High Availability
- [ ] Increase replicas for all services
- [ ] Use multiple Kafka brokers
- [ ] Set up PostgreSQL replication
- [ ] Configure anti-affinity rules

### Performance
- [ ] Tune Kafka partitions
- [ ] Optimize database indexes
- [ ] Implement caching (Redis)
- [ ] Use CDN for static assets

### Observability
- [ ] Set up distributed tracing (Jaeger)
- [ ] Configure log aggregation (ELK stack)
- [ ] Create custom Grafana dashboards
- [ ] Set up alerting rules

## 📞 Support

For issues:
1. Check logs: `./k8s/scripts/extract_logs.sh`
2. Review events: `kubectl get events -n uber-clone --sort-by='.lastTimestamp'`
3. Check pod status: `kubectl get pods -n uber-clone`
4. Verify Ingress: `kubectl get ingress -n uber-clone`

## 📖 Additional Documentation

- **[QUICKSTART.md](./QUICKSTART.md)**: Quick start guide
- **[ARCHITECTURE.md](./ARCHITECTURE.md)**: Detailed architecture
- **[CHECKLIST.md](./CHECKLIST.md)**: Deployment checklist
- **[../README.md](../README.md)**: Main project documentation
