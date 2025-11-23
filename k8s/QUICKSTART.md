# Kubernetes Quick Start Guide

Get the Uber-Clone application running on Kubernetes in under 5 minutes.

## ⚡ TL;DR

```bash
# One command to deploy everything
./k8s/scripts/deploy.sh
```

Access at: **`http://$(minikube ip)/`**

---

## 📋 Prerequisites Checklist

- [ ] Docker installed
- [ ] Minikube installed (`brew install minikube`)
- [ ] kubectl installed (`brew install kubectl`)
- [ ] At least 2 CPU cores and 4GB RAM available

## 🚀 Deployment Steps

### Step 1: Run Deployment Script

```bash
cd /path/to/uber-clone
./k8s/scripts/deploy.sh
```

This script automatically:
1. ✅ Starts Minikube (if not running)
2. ✅ Builds Docker images
3. ✅ Deploys Kafka + PostgreSQL
4. ✅ Deploys all microservices
5. ✅ Deploys frontend
6. ✅ Deploys monitoring stack (Prometheus & Grafana)
7. ✅ Waits for everything to be ready

**Duration:** ~3-5 minutes

### Step 2: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n uber-clone

# Should see all pods with status: Running (1/1)
```

### Step 3: Access Applications

**Option 1: Automatic Tunnel (Recommended)**
```bash
minikube service frontend -n uber-clone
```

**Option 2: Direct NodePort**
```bash
# Get Minikube IP
minikube ip
```

**Access URLs:**
- Frontend: `http://<MINIKUBE_IP>:30080`
- Rider App: `http://<MINIKUBE_IP>:30080/rider.html`
- Driver App: `http://<MINIKUBE_IP>:30080/driver.html`
- API Gateway: `http://<MINIKUBE_IP>:30001`
- Kafka UI: `http://<MINIKUBE_IP>:30090`
- Grafana: `http://<MINIKUBE_IP>:30030`

---

## 🎮 Using the Application

### Test Ride Flow

1. **Open Driver App:** `http://192.168.49.2/driver.html`
   - Select "John Doe"
   - Toggle status to **Online**
   - Click "Update Location"

2. **Open Rider App:** `http://192.168.49.2/rider.html`
   - Select "Alice Brown"
   - Enter pickup and destination
   - Click "Request Ride"

3. **Accept Ride (Driver App)**
   - Click "Accept" on the ride request
   - Click "Start Ride"
   - Click "Complete Ride"

4. **Watch Real-Time (Tracking Page):** `http://192.168.49.2/tracking.html`
   - See all online drivers on the map
   - Watch live location updates

---

## 🔍 Monitoring

### Check Logs

```bash
# All services at once
./k8s/scripts/extract_logs.sh
# Logs saved to k8s/logs/

# Single service
kubectl logs -f deployment/api-gateway -n uber-clone
```

### View Metrics

**Grafana:** `http://$(minikube ip)/grafana/`
- Username: `admin`
- Password: `admin`

**Prometheus:** `http://$(minikube ip)/prometheus/`

**Kafka UI:** `http://$(minikube ip)/kafka-ui/`

---

## 🛠️ Common Commands

### Status Checks

```bash
# Get all pods
kubectl get pods -n uber-clone

# Get all services  
kubectl get svc -n uber-clone

# Get Ingress
kubectl get ingress -n uber-clone

# Watch pods in real-time
kubectl get pods -n uber-clone -w
```

### Debugging

```bash
# Describe a pod (shows events)
kubectl describe pod <pod-name> -n uber-clone

# View logs
kubectl logs <pod-name> -n uber-clone

# Shell into a pod
kubectl exec -it <pod-name> -n uber-clone -- /bin/bash
```

### Scaling

```bash
# Scale a service to 2 replicas
kubectl scale deployment api-gateway -n uber-clone --replicas=2

# Scale all services
kubectl scale deployment --all -n uber-clone --replicas=2
```

---

## 🧹 Cleanup

### Remove Everything

```bash
./k8s/scripts/cleanup.sh
```

Or manually:

```bash
# Delete namespace (removes all resources)
kubectl delete namespace uber-clone

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

---

## ❓ Troubleshooting

### Pods Not Starting

**Problem:** Pods stuck in `Pending` status

**Solution:**
```bash
# Check available resources
kubectl describe pod <pod-name> -n uber-clone

# If insufficient CPU/memory, reduce replicas
kubectl scale deployment --all -n uber-clone --replicas=1

# Or increase Minikube resources
minikube stop
minikube start --cpus=4 --memory=8192
```

### Pods Crashing

**Problem:** Pods in `CrashLoopBackOff`

**Solution:**
```bash
# View logs
kubectl logs <pod-name> -n uber-clone --previous

# Common causes:
# 1. Kafka not ready - Wait ~60 seconds for Kafka to start
# 2. Database not ready - Wait for PostgreSQL to be Running
# 3. Config error - Check kubectl get configmap -n uber-clone
```

### Can't Access Services

**Problem:** Can't access services via browser

**Solution:**
```bash
# Check Ingress is running
kubectl get ingress -n uber-clone
kubectl get pods -n ingress-nginx

# Restart Ingress
minikube addons disable ingress
minikube addons enable ingress

# Or use NodePort fallback
open "http://$(minikube ip):30080"  # Frontend
```

### Images Not Found

**Problem:** `ImagePullBackOff` errors

**Solution:**
```bash
# Rebuild images in Minikube's Docker
eval $(minikube docker-env)
./k8s/scripts/build.sh
```

---

## 📚 More Documentation

- **[Full Kubernetes Guide](README.md)**: Detailed deployment documentation
- **[Architecture Guide](../ARCHITECTURE.md)**: System architecture details
- **[Main README](../README.md)**: Project overview

---

## 🎯 What's Next?

1. ✅ Deploy the application → **You are here!**
2. 📊 Explore monitoring dashboards
3. 🧪 Test the ride flow  
4. 📖 Read the architecture docs
5. 🚀 Deploy to a real Kubernetes cluster

---

**Need help?** Check the [troubleshooting section](#-troubleshooting) or open an issue.
