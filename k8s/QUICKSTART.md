# Kubernetes Quick Start

Get the Uber-Clone running on Kubernetes in 3 commands!

## 🚀 Quick Deploy

```bash
# 1. Run the deployment script
./k8s/scripts/deploy.sh

# 2. Wait for all pods to be ready (check status)
kubectl get pods -n uber-clone -w

# 3. Open the app
minikube service frontend -n uber-clone
```

That's it! The script will:
- ✅ Start Minikube
- ✅ Build Docker images
- ✅ Deploy all services
- ✅ Show you access URLs

## 📱 Accessing the App

Once deployed, you can access:

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Open in browser
open http://$MINIKUBE_IP:30080/rider.html   # Rider app
open http://$MINIKUBE_IP:30080/driver.html  # Driver app
open http://$MINIKUBE_IP:30090              # Kafka UI
open http://$MINIKUBE_IP:30030              # Grafana (admin/admin)
```

Or use shortcuts:

```bash
minikube service frontend -n uber-clone    # Opens frontend
minikube service kafka-ui -n uber-clone    # Opens Kafka UI
minikube service grafana -n uber-clone     # Opens Grafana
```

## 🔍 Monitoring

```bash
# View all pods
kubectl get pods -n uber-clone

# View logs for API Gateway
kubectl logs -f deployment/api-gateway -n uber-clone

# View logs for all services
kubectl logs -f -l app=ride-service -n uber-clone
```

## 🧹 Cleanup

```bash
# Remove everything
./k8s/scripts/cleanup.sh

# Or manually
kubectl delete namespace uber-clone
minikube stop
minikube delete
```

## 📚 Detailed Documentation

For detailed documentation, see [k8s/README.md](README.md)

## 🔧 Manual Steps (if script fails)

If the deploy script fails, you can deploy manually:

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192

# 2. Build images
eval $(minikube docker-env)
docker build -t uber-clone:latest .
docker build -t uber-clone-frontend:latest -f Dockerfile.frontend .

# 3. Deploy
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secrets.yaml
kubectl apply -f k8s/10-kafka.yaml
kubectl apply -f k8s/11-postgres.yaml
kubectl apply -f k8s/12-kafka-ui.yaml

# Wait for infrastructure
kubectl wait --for=condition=ready pod -l app=kafka -n uber-clone --timeout=120s
kubectl wait --for=condition=ready pod -l app=postgres -n uber-clone --timeout=120s

# Deploy services
kubectl apply -f k8s/20-api-gateway.yaml
kubectl apply -f k8s/21-ride-service.yaml
kubectl apply -f k8s/22-driver-service.yaml
kubectl apply -f k8s/23-matching-service.yaml
kubectl apply -f k8s/24-location-service.yaml
kubectl apply -f k8s/25-payment-service.yaml
kubectl apply -f k8s/30-frontend.yaml
kubectl apply -f k8s/40-prometheus.yaml
kubectl apply -f k8s/41-grafana.yaml
```

## 🐛 Troubleshooting

### Images not found
```bash
# Make sure you've pointed Docker to Minikube
eval $(minikube docker-env)
# Then rebuild
./k8s/scripts/build.sh
```

### Pods stuck in Pending
```bash
# Check events
kubectl describe pod <pod-name> -n uber-clone

# Likely need more resources
minikube stop
minikube start --cpus=4 --memory=10240
```

### Can't access services
```bash
# Make sure Minikube is running
minikube status

# Get the IP
minikube ip

# Check service is exposed
kubectl get svc -n uber-clone
```
