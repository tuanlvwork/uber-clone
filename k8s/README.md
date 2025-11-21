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

## 🚀 Quick Start

### 1. Start Minikube

```bash
# Start with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

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

### 3. Deploy to Kubernetes

```bash
# Apply all manifests in order
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secrets.yaml
kubectl apply -f k8s/10-kafka.yaml
kubectl apply -f k8s/11-postgres.yaml
kubectl apply -f k8s/12-kafka-ui.yaml
kubectl apply -f k8s/20-api-gateway.yaml
kubectl apply -f k8s/21-ride-service.yaml
kubectl apply -f k8s/22-driver-service.yaml
kubectl apply -f k8s/23-matching-service.yaml
kubectl apply -f k8s/24-location-service.yaml
kubectl apply -f k8s/25-payment-service.yaml
kubectl apply -f k8s/30-frontend.yaml
kubectl apply -f k8s/40-prometheus.yaml
kubectl apply -f k8s/41-grafana.yaml

# Or apply all at once
kubectl apply -f k8s/
```

### 4. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n uber-clone

# Watch pods starting up
kubectl get pods -n uber-clone -w

# Check services
kubectl get svc -n uber-clone
```

Wait until all pods show `Running` status (this may take 2-3 minutes).

### 5. Access the Application

```bash
# Get Minikube IP
minikube ip

# Access services via NodePort
# Frontend: http://<MINIKUBE_IP>:30080
# Kafka UI: http://<MINIKUBE_IP>:30090
# Prometheus: http://<MINIKUBE_IP>:30090
# Grafana: http://<MINIKUBE_IP>:30030
```

Or use `minikube service` for easy access:

```bash
# Open frontend in browser
minikube service frontend -n uber-clone

# Open Kafka UI
minikube service kafka-ui -n uber-clone

# Open Grafana
minikube service grafana -n uber-clone
```

## 📊 Architecture Overview

### Infrastructure Layer
- **Kafka** (StatefulSet): Message broker with persistent storage
- **PostgreSQL** (StatefulSet): Relational database with persistent storage
- **Kafka UI**: Web interface for Kafka management

### Application Layer
- **API Gateway** (2 replicas): REST API and WebSocket gateway
- **Ride Service** (2 replicas): Manages ride lifecycle
- **Driver Service** (2 replicas): Manages driver availability
- **Matching Service** (2 replicas): Matches riders with drivers
- **Location Service** (2 replicas): Tracks real-time location
- **Payment Service** (2 replicas): Handles payment processing

### Frontend Layer
- **Frontend** (2 replicas): Static files served via Nginx with API proxy

### Monitoring Layer
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

## 🔍 Monitoring and Debugging

### View Logs

```bash
# View logs for a specific service
kubectl logs -f deployment/api-gateway -n uber-clone

# View logs for all pods of a service
kubectl logs -f -l app=ride-service -n uber-clone

# View logs from init containers
kubectl logs <pod-name> -c wait-for-kafka -n uber-clone
```

### Port Forwarding

```bash
# Forward API Gateway to localhost
kubectl port-forward -n uber-clone svc/api-gateway 8001:8001

# Forward PostgreSQL
kubectl port-forward -n uber-clone svc/postgres 5432:5432

# Forward Kafka
kubectl port-forward -n uber-clone svc/kafka 9092:9092
```

### Execute Commands in Pods

```bash
# Get a shell in a pod
kubectl exec -it deployment/api-gateway -n uber-clone -- /bin/bash

# Run a one-off command
kubectl exec deployment/api-gateway -n uber-clone -- python --version
```

### Check Resource Usage

```bash
# View resource usage by pods
kubectl top pods -n uber-clone

# View resource usage by nodes
kubectl top nodes
```

## 🔧 Configuration

### Environment Variables

Edit `k8s/01-configmap.yaml` to modify:
- Kafka bootstrap servers
- Database connection strings
- Service URLs

### Secrets

Edit `k8s/02-secrets.yaml` to modify:
- Database credentials
- Grafana admin password

After changes, reapply:

```bash
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secrets.yaml

# Restart deployments to pick up changes
kubectl rollout restart deployment -n uber-clone
```

## 📈 Scaling

### Scale Microservices

```bash
# Scale API Gateway to 3 replicas
kubectl scale deployment api-gateway -n uber-clone --replicas=3

# Scale all microservices
kubectl scale deployment --all -n uber-clone --replicas=3
```

### Autoscaling (HPA)

```bash
# Enable metrics server
minikube addons enable metrics-server

# Create HPA for API Gateway
kubectl autoscale deployment api-gateway -n uber-clone \
  --cpu-percent=70 --min=2 --max=5

# View HPA status
kubectl get hpa -n uber-clone
```

## 🧹 Cleanup

### Delete All Resources

```bash
# Delete the entire namespace
kubectl delete namespace uber-clone

# Or delete resources individually
kubectl delete -f k8s/
```

### Stop Minikube

```bash
# Stop the cluster
minikube stop

# Delete the cluster (removes all data)
minikube delete
```

## 🐛 Troubleshooting

### Pods stuck in `Pending`

```bash
# Check pod events
kubectl describe pod <pod-name> -n uber-clone

# Common causes:
# - Insufficient resources (increase Minikube memory/CPU)
# - PVC not bound (check storage)
```

### Pods stuck in `CrashLoopBackOff`

```bash
# View logs
kubectl logs <pod-name> -n uber-clone --previous

# Common causes:
# - Dependencies not ready (Kafka/Postgres)
# - Configuration errors
# - Application bugs
```

### Init containers failing

```bash
# Check init container logs
kubectl logs <pod-name> -c <init-container-name> -n uber-clone

# Common causes:
# - Kafka/Postgres not ready
# - Network policies blocking access
```

### Image pull errors

```bash
# Ensure you've built images in Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t uber-clone:latest .
```

### Database connection issues

```bash
# Verify Postgres is running
kubectl get pods -n uber-clone | grep postgres

# Check Postgres logs
kubectl logs statefulset/postgres -n uber-clone

# Test connectivity from a pod
kubectl exec deployment/api-gateway -n uber-clone -- \
  nc -zv postgres 5432
```

## 🎯 Next Steps

1. **Set up Ingress**: Replace NodePort with Ingress for production-like routing
2. **Enable TLS**: Add cert-manager for HTTPS
3. **Add Persistent Volumes**: Use proper PV/PVC for production
4. **Implement Network Policies**: Restrict pod-to-pod communication
5. **Add Resource Quotas**: Prevent resource exhaustion
6. **Set up CI/CD**: Automate builds and deployments
7. **Configure Backup**: Back up Kafka and Postgres data

## 📚 Useful Commands

```bash
# Get all resources in namespace
kubectl get all -n uber-clone

# Describe a resource
kubectl describe <resource-type> <resource-name> -n uber-clone

# Edit a resource
kubectl edit <resource-type> <resource-name> -n uber-clone

# View events
kubectl get events -n uber-clone --sort-by='.lastTimestamp'

# Delete a stuck pod
kubectl delete pod <pod-name> -n uber-clone --force --grace-period=0

# Restart a deployment
kubectl rollout restart deployment <deployment-name> -n uber-clone

# Check rollout status
kubectl rollout status deployment <deployment-name> -n uber-clone
```

## 🔐 Security Best Practices

1. **Use Secrets**: Never hardcode credentials in ConfigMaps
2. **RBAC**: Implement Role-Based Access Control
3. **Network Policies**: Restrict inter-pod communication
4. **Pod Security Policies**: Enforce security standards
5. **Image Scanning**: Scan images for vulnerabilities
6. **Resource Limits**: Always set resource limits
7. **Read-only Root Filesystem**: Where possible

## 📞 Support

For issues or questions:
1. Check logs: `kubectl logs -n uber-clone`
2. Check events: `kubectl get events -n uber-clone`
3. Review pod status: `kubectl describe pod -n uber-clone`
4. Check resource usage: `kubectl top pods -n uber-clone`
