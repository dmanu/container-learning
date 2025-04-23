# Docker Lab: API Monitoring with Prometheus and Grafana

This lab demonstrates how to set up a complete monitoring solution for a containerized application using Docker, Prometheus, and Grafana.

## Components

- **Web**: NGINX web server serving static content
- **API**: Flask API with Prometheus metrics
- **Database**: PostgreSQL database
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards

## Getting Started

1. Start all services:

```bash
docker-compose up -d
```

2. Access the services:

- Web UI: http://localhost:8080
- API: http://localhost:5001
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (username: admin, password: admin)

## API Endpoints

- `/` - Basic hello message
- `/api/data` - Sample data endpoint (monitored with custom metrics)
- `/api/health` - Health check endpoint (monitored with custom metrics)
- `/metrics` - Prometheus metrics endpoint

## Monitoring Setup

The monitoring setup is fully automated:

1. The API exposes metrics using the `prometheus-flask-exporter` library
2. Prometheus is configured to scrape metrics from the API
3. Grafana is pre-configured with:
   - Prometheus data source
   - API monitoring dashboard

## Dashboard Details

The pre-configured dashboard includes:

- API request rate
- API response time
- API data request counter
- API health status

## Testing the Monitoring

To generate some metrics for visualization:

```bash
# Make some requests to the API
for i in {1..50}; do 
  curl http://localhost:5001/
  curl http://localhost:5001/api/data
  curl http://localhost:5001/api/health
  sleep 0.5
done
```

Then visit the Grafana dashboard to see the metrics visualization.
