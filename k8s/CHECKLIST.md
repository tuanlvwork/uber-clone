# ✅ Kubernetes Deployment Checklist

Use this checklist when deploying the Uber-Clone application to Kubernetes.

## 📋 Pre-Deployment

- [ ] Docker installed and running
- [ ] Minikube installed (`brew install minikube`)
- [ ] kubectl installed (`brew install kubectl`)
- [ ] Sufficient system resources (4 CPU cores, 8 GB RAM minimum)
- [ ] Port 30080, 30090, 30030 available on your machine

## 🏗️ Initial Setup

- [ ] Clone the repository
- [ ] Navigate to project directory
- [ ] Review `k8s/README.md` for detailed documentation
- [ ] Review `k8s/QUICKSTART.md` for quick instructions

## 🚀 Deployment Steps

### Option 1: Automated (Recommended)

- [ ] Run `./k8s/scripts/deploy.sh`
- [ ] Wait for script to complete (~3-5 minutes)
- [ ] Verify all pods are running: `kubectl get pods -n uber-clone`

### Option 2: Manual

- [ ] Start Minikube: `minikube start --cpus=4 --memory=8192`
- [ ] Point Docker to Minikube: `eval $(minikube docker-env)`
- [ ] Build images: `./k8s/scripts/build.sh`
- [ ] Apply namespace: `kubectl apply -f k8s/00-namespace.yaml`
- [ ] Apply config: `kubectl apply -f k8s/01-configmap.yaml k8s/02-secrets.yaml`
- [ ] Deploy infrastructure: `kubectl apply -f k8s/10-kafka.yaml k8s/11-postgres.yaml k8s/12-kafka-ui.yaml`
- [ ] Wait for infrastructure: `kubectl wait --for=condition=ready pod -l app=kafka -n uber-clone --timeout=120s`
- [ ] Deploy services: `kubectl apply -f k8s/20-*.yaml k8s/2[1-5]-*.yaml`
- [ ] Deploy frontend: `kubectl apply -f k8s/30-frontend.yaml`
- [ ] Deploy monitoring: `kubectl apply -f k8s/40-*.yaml k8s/41-*.yaml`

## ✓ Verification Steps

- [ ] All pods are running: `kubectl get pods -n uber-clone`
- [ ] All services are created: `kubectl get svc -n uber-clone`
- [ ] StatefulSets have PVCs: `kubectl get pvc -n uber-clone`
- [ ] No pods in CrashLoopBackOff or Error state
- [ ] Check logs for errors: `kubectl logs -l app=api-gateway -n uber-clone`

## 🌐 Access Verification

- [ ] Get Minikube IP: `minikube ip`
- [ ] Frontend accessible: `http://<MINIKUBE_IP>:30080`
- [ ] Rider app loads: `http://<MINIKUBE_IP>:30080/rider.html`
- [ ] Driver app loads: `http://<MINIKUBE_IP>:30080/driver.html`
- [ ] Kafka UI accessible: `http://<MINIKUBE_IP>:30090`
- [ ] Grafana accessible: `http://<MINIKUBE_IP>:30030` (admin/admin)

## 🧪 Functional Testing

- [ ] Register a rider from rider.html
- [ ] Register a driver from driver.html
- [ ] Set driver to "Available"
- [ ] Request a ride from rider interface
- [ ] Verify ride appears in Kafka UI (ride-requests topic)
- [ ] Driver receives ride request
- [ ] Driver can accept ride
- [ ] Ride status updates in real-time
- [ ] Check metrics in Grafana

## 📊 Monitoring Setup

- [ ] Prometheus scraping all services: Check `http://<MINIKUBE_IP>:30090/targets`
- [ ] Grafana data source configured
- [ ] Import dashboards (if available)
- [ ] Verify metrics are being collected

## 🔧 Configuration Validation

- [ ] ConfigMap values are correct: `kubectl get configmap uber-config -n uber-clone -o yaml`
- [ ] Secrets are set: `kubectl get secret uber-secrets -n uber-clone -o yaml`
- [ ] Environment variables injected correctly in pods
- [ ] Database connection successful: Check API Gateway logs

## 📈 Performance Checks

- [ ] Check resource usage: `kubectl top pods -n uber-clone`
- [ ] Check node usage: `kubectl top nodes`
- [ ] Ensure no pods are being OOMKilled
- [ ] Verify CPU/Memory within limits

## 🐛 Troubleshooting (if needed)

- [ ] View pod events: `kubectl describe pod <pod-name> -n uber-clone`
- [ ] Check init container logs: `kubectl logs <pod-name> -c <init-container> -n uber-clone`
- [ ] View recent events: `kubectl get events -n uber-clone --sort-by='.lastTimestamp'`
- [ ] Port-forward for debugging: `kubectl port-forward svc/api-gateway 8001:8001 -n uber-clone`
- [ ] Exec into pod: `kubectl exec -it deployment/api-gateway -n uber-clone -- /bin/bash`

## 📝 Post-Deployment

- [ ] Document any custom configurations
- [ ] Save Minikube IP for team members
- [ ] Set up monitoring alerts (optional)
- [ ] Configure autoscaling (optional)
- [ ] Back up Kafka and PostgreSQL data (for persistent deployments)

## 🎯 Optional Enhancements

- [ ] Enable Horizontal Pod Autoscaler: `minikube addons enable metrics-server`
- [ ] Set up HPA for services: `kubectl autoscale deployment <name> -n uber-clone --cpu-percent=70 --min=2 --max=5`
- [ ] Configure Ingress: `minikube addons enable ingress`
- [ ] Add custom Grafana dashboards
- [ ] Set up alerting rules in Prometheus

## 🧹 Cleanup Checklist

When you're done:

- [ ] Stop accepting traffic
- [ ] Export any important data
- [ ] Run cleanup script: `./k8s/scripts/cleanup.sh`
- [ ] Verify all resources deleted: `kubectl get all -n uber-clone`
- [ ] Stop Minikube: `minikube stop` (optional)
- [ ] Delete cluster: `minikube delete` (optional)

## 📞 Support Resources

If you encounter issues:

1. **Check logs**: `kubectl logs -n uber-clone <pod-name>`
2. **Review events**: `kubectl get events -n uber-clone`
3. **Consult docs**: See `k8s/README.md` for troubleshooting section
4. **Describe resources**: `kubectl describe <resource-type> <name> -n uber-clone`
5. **Check resource usage**: `kubectl top pods -n uber-clone`

## 📚 Documentation

- [Quick Start](QUICKSTART.md) - Get running in minutes
- [README](README.md) - Detailed deployment guide
- [ARCHITECTURE](ARCHITECTURE.md) - Architecture overview and diagrams
- [Main README](../README.md) - Project overview

---

## ✨ Quick Commands Reference

```bash
# Deploy
./k8s/scripts/deploy.sh

# Check status
kubectl get all -n uber-clone

# View logs
kubectl logs -f deployment/api-gateway -n uber-clone

# Access frontend
minikube service frontend -n uber-clone

# Clean up
./k8s/scripts/cleanup.sh
```

---

**Last Updated**: 2025-11-22
**Version**: 1.0.0
