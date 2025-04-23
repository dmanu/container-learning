from flask import Flask, jsonify
from prometheus_client import Gauge
from prometheus_flask_exporter import PrometheusMetrics
import os
import random
import time
import psycopg2

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Static information as metric
metrics.info('app_info', 'Application info', version='1.0.0')

# Create a direct gauge for health status
api_health = Gauge('api_health', 'Health status of API (1=up, 0=down)')
# Set initial health status to 1 (up)
api_health.set(1)

# Request count and latency as default metrics
@app.route('/')
def home():
    return jsonify({"message": "Hello from API"})

# Custom metrics
@app.route('/api/data')
@metrics.counter('api_data_requests', 'Number of requests to data endpoint')
def data():
    # Simulate variable response time
    time.sleep(random.random() * 0.2)
    return jsonify({"data": "Sample data from API"})

def check_db_connection():
    """Check if database connection is working"""
    try:
        # Get database connection details from environment variables
        db_host = os.environ.get('DB_HOST', 'db')
        db_user = os.environ.get('POSTGRES_USER', 'appuser')
        db_password = os.environ.get('POSTGRES_PASSWORD', 'secret')
        db_name = os.environ.get('POSTGRES_DB', 'appdb')
        
        # Try to connect to the database
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name,
            connect_timeout=3
        )
        conn.close()
        return True
    except Exception as e:
        app.logger.error(f"Database connection failed: {e}")
        return False

@app.route('/api/health')
def health():
    """
    Health check endpoint that checks:
    1. Database connectivity
    2. API service status
    """
    # Check database connection
    db_healthy = check_db_connection()
    
    # Update the health metric based on actual system state
    if db_healthy:
        api_health.set(1)
        status = "healthy"
    else:
        api_health.set(0)
        status = "unhealthy"
    
    # Return health status
    return jsonify({
        "status": status,
        "checks": {
            "database": "up" if db_healthy else "down"
        }
    })

if __name__ == '__main__':
    # Important: debug=False for metrics to work properly
    app.run(host='0.0.0.0', port=5000, debug=False)
