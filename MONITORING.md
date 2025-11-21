# Monitoring with Prometheus and Grafana

This project includes a monitoring stack using Prometheus and Grafana to track the health and performance of the microservices.

## Architecture

- **Prometheus**: Scrapes metrics from the Python microservices.
- **Grafana**: Visualizes the metrics collected by Prometheus.
- **Python Services**: Instrumented with `prometheus-client` and `prometheus-fastapi-instrumentator` to expose metrics.

## Accessing the Dashboards

1.  **Prometheus**: [http://localhost:9090](http://localhost:9090)
    -   Use this to query raw metrics and verify targets are up.
    -   Go to **Status > Targets** to see if all services are being scraped successfully.

2.  **Grafana**: [http://localhost:3000](http://localhost:3000)
    -   **Username**: `admin`
    -   **Password**: `admin` (You will be asked to change this on first login)
    -   **Data Source**: Prometheus is pre-configured as a data source.

## Metrics Exposed

### API Gateway (Port 8001)
-   Standard HTTP metrics (requests, latency, errors) provided by `prometheus-fastapi-instrumentator`.

### Microservices (Ports 8002-8005)
-   Standard Python process metrics (CPU, memory, GC).
-   You can add custom metrics (counters, gauges, histograms) to the services using `prometheus_client`.

## Service Ports for Metrics

| Service | Port | Metric Endpoint |
| :--- | :--- | :--- |
| API Gateway | 8001 | `/metrics` |
| Ride Service | 8002 | `/metrics` |
| Driver Service | 8003 | `/metrics` |
| Matching Service | 8004 | `/metrics` |
| Location Service | 8005 | `/metrics` |

## Setup

The monitoring stack is part of the `docker-compose.yml` file. It starts automatically when you run:

```bash
./start.sh
```

If you want to restart only the monitoring services:

```bash
docker-compose up -d prometheus grafana
```
