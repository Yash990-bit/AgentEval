# Production Deployment Guide

This manual covers the steps for deploying the **AI Agent Behavior Simulator (AABS)** to single-host Docker Compose environments, Kubernetes clusters (via Helm), and managed cloud platforms (AWS and GCP).

---

## 1. Single-Host Docker Compose Deployment

For small sandboxes, staging environments, or single-host VM deployments:

1. **Clone project and configure variables**:
   Copy `.env.example` to `.env.production` in the project root:
   ```bash
   cp .env.example .env.production
   ```
   *Edit `.env.production` to change default passwords, configure Sentry DSN, and set secure keys.*

2. **Launch the stack**:
   Run the following command from the `infra/` directory:
   ```bash
   docker compose -f docker-compose.yml --env-file ../.env.production up --build -d
   ```

3. **Verify running containers**:
   ```bash
   docker compose ps
   ```

---

## 2. Kubernetes Multi-Node Deployment (Helm)

For production-grade clusters with horizontal scaling, high availability, and automated failover:

1. **Add helm secrets and configurations**:
   Configure `k8s/helm/aabs/values.yaml` to specify registry coordinates, TLS domains, and database usernames:
   ```yaml
   ingress:
     hosts:
       - host: aabs.yourdomain.com
         paths:
           - path: /
             pathType: Prefix
   sentry:
     dsn: "https://example@sentry.io/1234"
   ```

2. **Deploy the chart**:
   Create the target namespace and deploy the release:
   ```bash
   helm upgrade --install aabs ./k8s/helm/aabs \
     --namespace production \
     --create-namespace \
     --values ./k8s/helm/aabs/values.yaml
   ```

3. **Verify ingress TLS certificate**:
   Check if cert-manager has provisioned the Let's Encrypt certificates:
   ```bash
   kubectl get certificate -n production
   ```

---

## 3. Cloud Provider Best Practices

### A. AWS Deployment (ECS Fargate + RDS)
* **Compute (ECS)**: Run the `frontend`, `backend`, `worker`, and `beat` as ECS Fargate Task Definitions.
* **Database (RDS)**: Spin up an AWS RDS PostgreSQL instance (Multi-AZ enabled). Disable the local postgres container.
* **Cache (ElastiCache)**: Spin up an Amazon ElastiCache Redis cluster (with transit encryption enabled).
* **Storage (S3)**: Create a secure AWS S3 bucket and assign IAM Task Roles allowing read/write actions to the bucket. Set `S3_ENDPOINT` to `s3.amazonaws.com` in environment configurations.
* **Routing (ALB)**: Route traffic using an AWS Application Load Balancer integrated with ACM (AWS Certificate Manager) for HTTPS TLS termination.

### B. GCP Deployment (GKE + Cloud SQL)
* **Compute (GKE)**: Deploy the Helm chart onto a Google Kubernetes Engine (GKE) Standard cluster.
* **Database (Cloud SQL)**: Provision a Google Cloud SQL PostgreSQL instance and use the Cloud SQL Auth Proxy sidecar inside GKE pods for secure database sessions.
* **Cache (Memorystore)**: Run a Google Cloud Memorystore Redis instance.
* **Storage (GCS)**: Provision Google Cloud Storage buckets and authenticate via Workload Identity.
