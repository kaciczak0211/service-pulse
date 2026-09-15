# ServicePulse 🚀

A lightweight, containerized uptime and service health monitoring platform built with **FastAPI**, **PostgreSQL**, **NGINX**, and **Docker**.

---

## Overview

ServicePulse is designed to monitor external and internal services via automated HTTP synthetic health checks. It provides a RESTful API for registering endpoints, executing health probes, and persisting uptime/downtime states in a relational database.

---

## Current Architecture (Phase 2)

The system operates as a multi-container environment orchestrated with **Docker Compose**, guarded by an **NGINX Reverse Proxy** as the single public entrypoint:

```text
[ Client / Browser ]
         │
         ▼  (Host port :80 - Standard HTTP)
┌──────────────────────────────────────────────────────────────┐
│ Docker Bridge Network                                        │
│                                                              │
│   ┌────────────────────────────────────────┐                 │
│   │ service-pulse-nginx (NGINX Alpine)     │                 │
│   │ - Edge Reverse Proxy & Web Server      │                 │
│   │ - Preserves Client IP Headers          │                 │
│   │ - Hides Internal Application Topology  │                 │
│   └───────────────────┬────────────────────┘                 │
│                       │                                      │
│                       ▼ (Internal DNS: service-pulse:8000)   │
│   ┌────────────────────────────────────────┐                 │
│   │ service-pulse (FastAPI)                │                 │
│   │ - REST API & Synthetic HTTP Probes     │                 │
│   │ - SQLAlchemy ORM                       │                 │
│   │ - Internal Only (No host ports exposed)│                 │
│   └───────────────────┬────────────────────┘                 │
│                       │                                      │
│                       ▼ (Internal DNS: db:5432)              │
│   ┌────────────────────────────────────────┐                 │
│   │ service-pulse-db (PostgreSQL 16)       │                 │
│   │ - Relational Storage                   │                 │
│   │ - Named Volume Persistence             │                 │
│   └────────────────────────────────────────┘                 │
└──────────────────────────────────────────────────────────────┘
```

### Key Engineering Features Implemented:
- **Edge Reverse Proxy (NGINX)**:
  - Serves as the single ingress point on port `80`, routing traffic to the internal `service-pulse` upstream.
  - Passes essential proxy headers (`X-Real-IP`, `X-Forwarded-For`, `Host`, `X-Forwarded-Proto`) to maintain client transparency.
  - Isolates and shields application runtime from direct public network exposure.
- **Container Isolation & Networking**:
  - Inter-service communication handled via Docker's internal bridge network and embedded DNS resolution (`service-pulse:8000`, `db:5432`).
- **Data Persistence**:
  - PostgreSQL state persisted using Docker named volumes (`postgres_data`) to prevent data loss across container restarts.
- **Dynamic Dependency Orchestration**:
  - Health checks (`pg_isready`) and conditional startup (`depends_on: condition: service_healthy`) to ensure database availability prior to API boot.
- **Synthetic Monitoring Engine**:
  - HTTP probe engine evaluating response status codes (2xx/3xx vs 4xx/5xx/timeout) to determine real-time `UP` / `DOWN` service availability.

---

## API Reference

Interactive API documentation (Swagger UI) is available through the NGINX reverse proxy at:
**`http://localhost/docs`**

### Key Endpoints:
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | API heartbeat check |
| `GET` | `/services` | List all registered services and their current status |
| `POST` | `/services` | Register a new service to monitor (`name`, `url`) |
| `POST` | `/services/{id}/check` | Trigger an active HTTP probe and update service status in PostgreSQL |

---

## Getting Started

### Prerequisites:
- Docker & Docker Compose installed.

### Running Locally:
1. Clone the repository:
   ```bash
   git clone https://github.com/kaciczak0211/service-pulse.git
   cd service-pulse
   ```

2. Start the services:
   ```bash
   docker compose up -d --build
   ```

3. Verify status:
   ```bash
   docker compose ps
   ```

4. Stream live multi-container logs:
   ```bash
   docker compose logs -f nginx service-pulse
   ```

---

## Roadmap

- [x] **Phase 1**: Containerization & Persistence (FastAPI + PostgreSQL + Docker Compose)
- [x] **Phase 2**: Reverse Proxy & Edge Routing with NGINX
- [ ] **Phase 3**: Container Security & Process Management (non-root execution, Linux signals, backup scripts)
- [ ] **Phase 4**: Automated CI/CD Pipeline via GitHub Actions
- [ ] **Phase 5**: Orchestration with Kubernetes (K8s Manifests: Deployments, Services, ConfigMaps)
- [ ] **Phase 6**: Observability & Metrics Export (Prometheus format)
- [ ] **Phase 7**: Infrastructure as Code (Terraform provisioning on LocalStack / AWS)
