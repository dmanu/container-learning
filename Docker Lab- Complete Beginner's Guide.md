# Docker Lab: Complete Beginner's Guide

Welcome! This is a detailed, step-by-step guide to learning Docker through a practical, hands-on project. By the end, you’ll have built and run a multi-container application with a backend API, database, monitoring, a VPN, and a privacy browser stack. Every command is written out with explanations to help beginners understand exactly what's happening.

This guide assumes you are on **macOS** and have **Docker Desktop** installed and running. You can verify this by running:
```bash
docker --version
```
You should see output like:
```
Docker version 24.0.5, build ced0996
```

Let’s begin!

---

## Step 1: Running Your First Container

**Goal:** Confirm Docker is installed and working.

### 1.1 Run a test container
```bash
docker run hello-world
```
This command tells Docker to fetch the `hello-world` image from Docker Hub and run it. You should see output like this:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```
If you see this, you're ready to move on!

---

## Step 2: Exploring Containers

**Goal:** Understand what a container is and how to interact with it.

### 2.1 Start an Alpine container interactively
```bash
docker run -it alpine sh
```
- `-it`: allows you to interact with the shell
- `alpine`: a tiny Linux distribution
- `sh`: runs the shell

You are now inside a Linux container! Try some basic commands:
```sh
uname -a
ls /
```

### 2.2 Install a package in the container
```sh
apk update
apk add curl
curl https://example.com
```
You'll see raw HTML from the site. You're making HTTP requests from inside your container.

Exit with:

```bash
exit
```

---

## Step 3: Build a Static Web App Container

**Goal:** Package a static website into a Docker image.

### 3.1 Set up your project directory
```bash
mkdir docker-lab
cd docker-lab
mkdir static-site
cd static-site
echo '<h1>Hello from Docker</h1>' > index.html
```

### 3.2 Write a Dockerfile
Create a file called `Dockerfile` with the following content:

```Dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
```

You can use your favourite text editor (e.g. vi or nano) or use the command:

```bash
echo 'FROM nginx:alpine\n\rCOPY . /usr/share/nginx/html' > Dockerfile
```

This Dockerfile tells Docker to use the `nginx` web server and copy your `index.html` into its web directory.

### 3.3 Build the image
```bash
docker build -t static-site .
```
You’ll see step-by-step logs. At the end:
```
Successfully tagged static-site:latest
```

### 3.4 Run the container
```bash
docker run -d -p 8080:80 static-site
```
Now open `http://localhost:8080` in your browser — you should see your HTML page.

To stop the container:

```bash
docker ps
```
Copy the `CONTAINER ID`, then:

```bash
docker stop <CONTAINER ID>
```

Pro tip:  you only need to specify the first 2 or so characters of the ID, not the whole thing!

---

## Step 4: Convert to Docker Compose

**Goal:** Use Docker Compose to define and run containers.

### 4.1 Create `docker-compose.yml`
```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./static-site:/usr/share/nginx/html
```

This file defines a single service named `web` that runs an Nginx server.

### 4.2 Run it with Compose
```bash
docker compose up -d
```
You can now visit `http://localhost:8080`. 

To stop the containers:

```bash
docker compose down
```
---

## Step 5: Add a Backend API

**Goal:** Add a simple API server that serves JSON.

### 5.1 Create the API
```bash
mkdir api
cd api
```
Create `app.py`:

```python
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Hello from API"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

Create `requirements.txt`:

```
flask
```

Create a Dockerfile:

```Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

---

## Step 6: Full Stack with Compose (Frontend + API + DB)

### 6.1 Update `docker-compose.yml`
```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./static-site:/usr/share/nginx/html
    depends_on:
      - api

  api:
    build: ./api
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=db

  db:
    image: postgres
    environment:
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=appdb
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### 6.2 Launch the stack
```bash
docker compose up --build -d
```
Visit:

- `http://localhost:8080` (static site)
- `http://localhost:5000` (API)

---

## Step 7: Add Logging, Config, and Host Access

### 7.1 Add log mounts
Update the `web` service:

```yaml
    volumes:
      - ./static-site:/usr/share/nginx/html
      - ./logs:/var/log/nginx
```
Create the `logs` directory:

```bash
mkdir logs
```
Now if you re-run docker compose, logs written inside the container will appear on your host.

Try the command:

```bash
cat logs/* | less
```


### 7.2 Use exec to inspect containers
```bash
docker compose exec api sh
```
Inside the container, try:

```sh
env
cat app.py
```
Exit with:

```sh
exit
```

---

## Step 8: Monitoring with Prometheus and Grafana

### 8.1 Add Prometheus and Grafana

Add to `docker-compose.yml`:

```yaml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  pgdata:
  grafana-data:
```

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'docker'
    static_configs:
      - targets: ['api:5001']
```

and re-run docker compose:

```bash
docker compose up -d
```
Visit `http://localhost:3000`, log in with `admin/admin`.

---

## Step 9: Privacy Tools Stack (Firefox + Torrent + VPN)

### 9.1 Add services to Compose
```yaml
  gluetun:
    image: qmcgaw/gluetun
    cap_add:
      - NET_ADMIN
    environment:
      - VPN_SERVICE_PROVIDER=protonvpn
      - OPENVPN_USER=<your_user>
      - OPENVPN_PASSWORD=<your_pass>
    ports:
      - "8888:8888"

  qbittorrent:
    image: linuxserver/qbittorrent
    depends_on:
      - gluetun
    network_mode: service:gluetun
    environment:
      - WEBUI_PORT=8080
    ports:
      - "8080:8080"
    volumes:
      - ./downloads:/downloads

  firefox:
    image: jlesage/firefox
    depends_on:
      - gluetun
    network_mode: service:gluetun
    ports:
      - "5800:5800"
```
Start with:

```bash
docker compose up -d
```
Visit Firefox at `http://localhost:5800`, and qBittorrent at `http://localhost:8080`.

---

## Step 10: WireGuard VPN Server

### 10.1 Add WireGuard to Compose
```yaml
  wireguard:
    image: linuxserver/wireguard
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    environment:
      - PUID=1000
      - PGID=1000
      - SERVERURL=<your_url>
      - SERVERPORT=51820
    ports:
      - "51820:51820/udp"
    volumes:
      - ./wireguard-config:/config
      - /lib/modules:/lib/modules
```
Check logs for QR code to scan and connect.

---

## Step 11: Clean Up
```bash
docker compose down -v
```
This stops and removes containers, networks, and volumes.

---

**You did it!** You now understand container basics, Dockerfiles, Compose, networks, volumes, APIs, databases, logging, privacy stacks, and VPNs. Let me know when you want this in a visual, polished format!

