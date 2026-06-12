# AI Agent Behavior Simulator (AABS)

AABS is a production-grade multi-agent simulation sandbox and observability platform. It allows users to run simulated AI agent swarms, dynamically inject coordination failures/hazards, analyze relationships, and track composite resource performance metrics.

---

## 1. Quickstart (Docker Compose)

The fastest way to launch the complete local stack (Frontend, Backend Server, Celery Worker pools, Celery Beat, PostgreSQL, Redis, Qdrant Vector DB, and MinIO S3 Object Storage) is using Docker Compose:

1. **Clone project and create configuration variables**:
   ```bash
   cp .env.example .env.production
   ```
   *Edit `.env.production` to change default credentials if running in exposed staging spaces.*

2. **Spin up the stack**:
   ```bash
   docker compose -f infra/docker-compose.yml --env-file .env.production up --build -d
   ```

3. **Explore the Services**:
   * **Frontend UI**: [http://localhost:3000/](http://localhost:3000/)
   * **FastAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   * **MinIO Object Console**: [http://localhost:9001/](http://localhost:9001/)
   * **Qdrant Dashboard**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

## 2. Project Layout

```text
├── backend/            # FastAPI REST backend & Simulation Engine
├── frontend/           # Next.js & Tailwind CSS responsive portal
├── worker/             # Dedicated Celery worker configuration
├── k8s/                # Helm deployment manifests (Horizontal/Vertical autoscalers)
├── monitoring/         # Prometheus scrape rules, Alertmanager alerts & Grafana dashboards
├── logging/            # Loki & Promtail log collectors configuration
├── locust/             # Performance load testing script
├── docs/               # Advanced Architecture, Development, and API manuals
└── infra/              # Production-grade multi-stage Docker Compose setup
```

---

## 3. Operations & Architecture Manuals

For comprehensive guides on system topology, integrations, and deployment scripts, refer to the documents in the `docs/` folder:

1. **[Architecture Manual](file:///Users/yashraghubanshi/Desktop/AI-Agent%20Behaviour%20Simulator/docs/architecture.md)**: Details data flow diagrams, database selection rationales, and worker queues.
2. **[REST API Spec Reference](file:///Users/yashraghubanshi/Desktop/AI-Agent%20Behaviour%20Simulator/docs/api.md)**: Narrative of core FastAPI REST endpoints, rate limiting, and webhook event payloads.
3. **[Kubernetes & Multi-Cloud Deployment Guide](file:///Users/yashraghubanshi/Desktop/AI-Agent%20Behaviour%20Simulator/docs/deployment.md)**: Advanced installation steps for GKE, AWS ECS/Fargate, and Helm configurations.
4. **[Developer Guidelines](file:///Users/yashraghubanshi/Desktop/AI-Agent%20Behaviour%20Simulator/docs/development.md)**: Running local tests, adding agent parameters, and custom simulation events.
