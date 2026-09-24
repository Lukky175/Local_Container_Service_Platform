# Local Container Service Platform

A local container orchestration and load-balancing platform that deploys multiple instances of a Flask-based dummy service, distributes incoming requests across service instances, monitors service health and resource utilization, and automatically scales the number of containers based on configurable metrics.

The project is being developed as a local-first DevOps project. The architecture will later be extended toward a cloud deployment on AWS.

# Run the application
docker compose up --build
docker compose down

---

## 1. Problem Statement

> Develop a platform that deploys multiple instances of a dummy service across local containers and distributes requests using a load-balancing strategy. Students can additionally implement service health checking and automatic scaling as advanced features.

This project implements the core requirement and extends it with:

* Dynamic container discovery
* Service health checking
* Resource monitoring
* Metric-based automatic scaling
* Monitoring dashboards
* Load testing
* Container-level visibility
* Automation
* Documentation and architecture diagrams

---

## 2. Project Objective

The objective is to understand how modern container-based platforms handle:

1. Containerized application deployment
2. Multiple service instances
3. Reverse proxying and load balancing
4. Service discovery
5. Health checking
6. Resource monitoring
7. Automatic scaling
8. Fault handling
9. Infrastructure automation

The project will initially run completely locally using Docker Desktop and will later be extended toward AWS.

---

## 3. High-Level Architecture


                         Client
                           |
                           v
                  +------------------+
                  |     Traefik      |
                  | Reverse Proxy    |
                  | Load Balancer    |
                  +--------+---------+
                           |
                    Docker Network
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      +---------+      +---------+      +---------+
      | cont-1  |      | cont-2  |      | cont-3  |
      | Flask   |      | Flask   |      | Flask   |
      +---------+      +---------+      +---------+
          |                |                |
          +----------------+----------------+
                           |
                           v
                     Metrics Layer
                           |
              +------------+------------+
              |                         |
              v                         v
         Prometheus                  Grafana
              |
              v
       +--------------+
       |  Autoscaler  |
       |    Python    |
       +------+-------+
              |
              v
         Docker Engine
              |
        +-----+-----+
        |           |
     SCALE UP    SCALE DOWN


---

## 4. Technology Stack

### Application

* Python
* Flask
* HTML
* CSS
* JavaScript

The Flask application acts as the dummy service.

Each instance will expose information identifying the container serving the request.

Example:


{
  "service": "dummy-service",
  "container": "cont-2",
  "hostname": "7f83c12a",
  "status": "running"
}


### Containerization

* Docker
* Docker Desktop
* Docker Compose

Docker will be used to build and run isolated service instances.

### Reverse Proxy and Load Balancing

* Traefik

Traefik will act as the entry point to the platform and dynamically discover Docker services.

The Docker provider allows Traefik to watch the Docker environment and dynamically update routing when containers or services change.

### Monitoring

* Prometheus
* Grafana

Prometheus will collect metrics while Grafana will provide visualization dashboards.

### Autoscaling

A custom Python autoscaler will:

1. Read service/resource metrics
2. Compare metrics against configured thresholds
3. Determine the desired replica count
4. Request scaling through Docker
5. Enforce minimum and maximum replica limits
6. Apply cooldown periods to avoid rapid scaling oscillations

### Load Testing

Traffic will be generated using tools such as:

* curl
* Python HTTP scripts
* ApacheBench / similar benchmarking tools

---

# 5. Core Features

## 5.1 Multiple Service Instances

The platform will run multiple instances of the Flask service.

Initial configuration:


Minimum instances: 3


Example:


cont-1
cont-2
cont-3


Each container will expose its identity through the application response.

---

## 5.2 Load Balancing

Traefik will distribute incoming requests among available service instances.

For example:


Request 1 → cont-1
Request 2 → cont-2
Request 3 → cont-3
Request 4 → cont-1
Request 5 → cont-2


The behavior will be demonstrated through the service response.

---

## 5.3 Service Health Checking

The Flask application will provide:


/health


Example:


{
  "status": "healthy",
  "container": "cont-2"
}


Health checks will be used to identify unavailable or unhealthy service instances.

Unhealthy instances should not receive normal application traffic.

---

## 5.4 Metrics

The platform will monitor metrics such as:

* CPU utilization
* Memory utilization
* Request count
* Request rate
* Response latency
* Number of active instances
* Healthy instances
* Unhealthy instances

CPU utilization will initially be used as the primary autoscaling metric.

---

# 6. Automatic Scaling

The autoscaler will dynamically adjust the number of service instances.

Example configuration:


MIN_REPLICAS = 3
MAX_REPLICAS = 10

SCALE_UP_THRESHOLD = 70%
SCALE_DOWN_THRESHOLD = 30%


Example:


CPU = 35%
3 replicas
      ↓
No scaling


High load:


CPU = 78%
3 replicas
      ↓
Scale up
      ↓
4 replicas


Continued high load:


CPU = 82%
4 replicas
      ↓
Scale up
      ↓
5 replicas


Traffic decreases:


CPU = 25%
5 replicas
      ↓
Scale down
      ↓
4 replicas


The system will maintain the configured minimum and maximum replica limits.

---

# 7. Container Identity

Every application instance will receive a unique container identifier.

Examples:


cont-1
cont-2
cont-3
cont-4


This allows the load-balancing behavior to be directly observed.

Example:


{
  "container": "cont-4",
  "message": "Request served successfully"
}


The identifier will be provided through configuration/environment variables rather than being hard-coded into the application.

---

# 8. Platform Dashboard

A custom lightweight dashboard will eventually provide a high-level view of the platform.

The dashboard will display:

* Current replica count
* Healthy containers
* Unhealthy containers
* CPU utilization
* Memory utilization
* Request rate
* Response latency
* Autoscaler state
* Scaling events
* Individual container status

---

# 9. Project Development Phases

## Phase 1 — Basic Container Platform

Goal:


Flask
  ↓
Docker
  ↓
Multiple containers
  ↓
Traefik
  ↓
Load balancing


Tasks:

* Create Flask service
* Create Dockerfile
* Create service UI
* Add container identity
* Create Docker network
* Run multiple instances
* Configure Traefik
* Verify request distribution

---

## Phase 2 — Health Checking

Tasks:

* Implement `/health`
* Configure container health checks
* Simulate unhealthy instances
* Verify unhealthy instances are removed from traffic
* Document failure/recovery behavior

---

## Phase 3 — Monitoring

Tasks:

* Add Prometheus
* Expose application metrics
* Collect container/platform metrics
* Add Grafana
* Create monitoring dashboard

---

## Phase 4 — Load Generation

Tasks:

* Create traffic generator
* Generate controlled request load
* Observe CPU/resource changes
* Measure request rate and latency

---

## Phase 5 — Automatic Scaling

Tasks:

* Build Python autoscaler
* Read metrics
* Define scaling thresholds
* Implement scale-up logic
* Implement scale-down logic
* Implement minimum/maximum replicas
* Implement cooldown period
* Test scaling under load

---

## Phase 6 — Dynamic Platform Behavior

Tasks:

* Automatically discover newly created containers
* Integrate autoscaler with Docker
* Verify Traefik detects new instances
* Verify new instances receive traffic
* Verify removed instances stop receiving traffic

---

## Phase 7 — Platform Dashboard

Tasks:

* Build custom dashboard
* Display container information
* Display metrics
* Display health status
* Display scaling events
* Display current replica count

---

## Phase 8 — CI/CD

Future implementation:


Developer
   |
   v
GitHub
   |
   v
CI Pipeline
   |
   +-- Tests
   +-- Build Docker Image
   +-- Validation
   |
   v
Local Deployment


---

## Phase 9 — AWS Extension

After the local platform is stable, the architecture will be evaluated for cloud deployment.

Potential AWS technologies:

* EC2
* ECR
* VPC
* Security Groups
* Load Balancer
* CloudWatch
* Auto Scaling
* Terraform
* GitHub Actions

The exact AWS architecture will be decided after the local implementation is complete.

---

# 10. Repository Structure

Initial structure:


local-container-platform/
│
├── app/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── style.css
│       └── app.js
│
├── traefik/
│   └── traefik.yml
│
├── docker-compose.yml
│
├── README.md
│
└── docs/
    ├── architecture.md
    ├── load-balancing.md
    ├── health-checks.md
    ├── monitoring.md
    └── autoscaling.md


Later:


local-container-platform/
│
├── app/
├── traefik/
├── autoscaler/
├── monitoring/
│   ├── prometheus/
│   └── grafana/
│
├── load-generator/
├── dashboard/
├── docs/
├── docker-compose.yml
├── docker-compose.monitoring.yml
└── README.md


---

# 11. Expected Final Demonstration

The final demonstration should show the following sequence.

### Step 1 — Start platform


3 containers


### Step 2 — Send requests


Request → cont-1
Request → cont-2
Request → cont-3


### Step 3 — Break a container


cont-2 → unhealthy


Traffic should continue through healthy instances.

### Step 4 — Generate heavy traffic


CPU increases
      ↓
Autoscaler detects threshold
      ↓
3 → 4 containers


### Step 5 — Continue load


4 → 5 containers


### Step 6 — Reduce traffic


CPU decreases
      ↓
Autoscaler scales down
      ↓
5 → 4 → 3


### Step 7 — Observe everything

Grafana/custom dashboard shows:


Instances
Health
CPU
Memory
Requests
Latency
Scaling events


---

# 12. Learning Outcomes

This project is intended to provide practical understanding of:

* Docker
* Container networking
* Docker Compose
* Reverse proxies
* Load balancing
* Service discovery
* Health checks
* Monitoring
* Prometheus
* Grafana
* Autoscaling
* Docker API
* Infrastructure automation
* CI/CD
* Cloud architecture

---

# 13. Local Development Environment

The initial implementation will run on:


Windows
   ↓
Docker Desktop
   ↓
Linux containers


The project will remain local during the initial development phases.

A cloud deployment will be considered only after the local platform is functional and tested.

---

# 14. Future Direction

The local platform is intentionally designed as a learning foundation.

The final architecture may evolve toward:


Local Docker Platform
        ↓
Monitoring
        ↓
Autoscaling
        ↓
CI/CD
        ↓
AWS
        ↓
Infrastructure as Code


The objective is not only to satisfy the original assignment but to understand how the individual components of a container platform fit together.
