# ServicePulse 🚀

A lightweight, containerized uptime and service health monitoring platform built with **FastAPI**, **PostgreSQL**, and **Docker**.

---

## Overview

ServicePulse is designed to monitor external and internal services via automated HTTP synthetic health checks. It provides a RESTful API for registering endpoints, executing health probes, and persisting uptime/downtime states in a relational database.

---

## Current Architecture (Phase 1)

The system currently runs as a multi-container environment orchestrated with **Docker Compose**:

```text
[ Client / Browser ]
         │
         ▼  (Host port :8080)
┌──────────────────────────────────────────────┐
│ Docker Bridge Network                        │
│                                              │
│   ┌───────────────────────────┐              │
│   │ service-pulse (FastAPI)   │              │
│   │ - REST API                │              │
│   │ - HTTP Health Probes      │              │
│   │ - SQLAlchemy ORM          │              │
│   └─────────────┬─────────────┘              │
│                 │                            │
│                 ▼ (Internal DNS: db:5432)    │
│   ┌───────────────────────────┐              │
│   │ service-pulse-db          │              │
│   │ - PostgreSQL 16           │              │
│   │ - Named Volume Persistence│              │
│   └───────────────────────────┘              │
└──────────────────────────────────────────────┘
```

### Key Engineering Features Implemented:
- **Container Isolation & Networking**:
  - Services communicate over an internal Docker bridge network using Docker's embedded DNS server (`db:5432`), strictly isolating internal database traffic from the public network.
  - Decoupled container runtime (`localhost` loopback isolation).
- **Data Persistence**:
  - PostgreSQL state is persisted using Docker named volumes (`postgres_data`) to prevent data loss across container lifecycles.
- **Dynamic Dependency Orchestration**:
  - Implemented health checks (`pg_isready`) and conditional dependency startup (`depends_on: condition: service_healthy`) to ensure database readiness before API initialization.
- **Synthetic Monitoring Engine**:
  - HTTP probe engine with timeout protection that evaluates HTTP response status codes (2xx/3xx vs 4xx/5xx/network errors) to determine real-time `UP` / `DOWN` service availability.

---

## API Reference

Interactive API documentation (Swagger UI) is available at:
`http://localhost:8080/docs`

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

4. View logs:
   ```bash
   docker compose logs -f
   ```

---

## Roadmap

- [x] **Phase 1**: Containerization & Persistence (FastAPI + PostgreSQL + Docker Compose)
- [ ] **Phase 2**: Reverse Proxy & Edge Routing with Nginx
- [ ] **Phase 3**: Container Security & Process Management (non-root execution, Linux signals)
- [ ] **Phase 4**: Automated CI/CD Pipeline via GitHub Actions
- [ ] **Phase 5**: Orchestration with Kubernetes (K8s Manifests: Deployments, Services, ConfigMaps)
- [ ] **Phase 6**: Observability & Metrics Export (Prometheus format)
- [ ] **Phase 7**: Infrastructure as Code (Terraform provisioning on LocalStack / AWS)
