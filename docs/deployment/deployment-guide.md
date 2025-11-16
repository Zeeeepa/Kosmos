# Kosmos AI Scientist - Deployment Guide

This guide provides comprehensive instructions for deploying Kosmos in various environments, from local development to production cloud deployments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Production Deployment (Docker Compose)](#production-deployment-docker-compose)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Provider Guides](#cloud-provider-guides)
- [Monitoring & Observability](#monitoring--observability)
- [Security](#security)
- [Scaling](#scaling)
- [Backup & Disaster Recovery](#backup--disaster-recovery)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Overview

Kosmos AI Scientist supports multiple deployment patterns:

- **Local Development**: Single container with SQLite
- **Docker Compose**: Multi-container setup with PostgreSQL, Redis, Neo4j
- **Kubernetes**: Production-ready orchestration with auto-scaling
- **Cloud Platforms**: AWS ECS, GCP GKE, Azure AKS

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                         │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐            ┌────▼────┐
    │ Kosmos  │            │ Kosmos  │
    │ Instance│            │ Instance│
    │   #1    │            │   #2    │
    └────┬────┘            └────┬────┘
         │                       │
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼───┐      ┌────▼────┐      ┌────▼────┐
│PostGres│      │  Redis  │      │  Neo4j  │
│  DB    │      │  Cache  │      │  Graph  │
└────────┘      └─────────┘      └─────────┘
```

### Resource Requirements

**Minimum (Development)**:
- CPU: 2 cores
- Memory: 4 GB RAM
- Disk: 20 GB
- Network: 10 Mbps

**Recommended (Production)**:
- CPU: 8 cores
- Memory: 16 GB RAM
- Disk: 100 GB SSD
- Network: 100 Mbps

**Scaling (High-throughput)**:
- CPU: 16+ cores
- Memory: 32+ GB RAM
- Disk: 500 GB SSD
- Network: 1 Gbps

## Prerequisites

### Required Software

- **Docker**: 20.10+ ([Install Guide](https://docs.docker.com/get-docker/))
- **Docker Compose**: 2.0+ (included with Docker Desktop)
- **Git**: Latest version
- **Anthropic API Key**: From [console.anthropic.com](https://console.anthropic.com/)

### Optional Components

- **Kubernetes**: 1.24+ (for K8s deployments)
- **kubectl**: Kubernetes CLI
- **Helm**: Kubernetes package manager (v3+)
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

### Supported Platforms

- Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+)
- macOS (11+)
- Windows 10/11 (with WSL2)

## Prerequisites

### Docker Installation

Kosmos requires Docker for containerized deployment.

#### Automated Installation (WSL2)

For WSL2 users, we provide an automated installation script:

```bash
# Clone repository first
git clone https://github.com/jimmc414/Kosmos.git
cd Kosmos

# Run automated Docker installation
./scripts/setup_docker_wsl2.sh

# Or using Make
make setup-docker
```

**What it does:**
- ✓ Detects WSL2 environment
- ✓ Adds Docker's official repository
- ✓ Installs Docker Engine and Compose plugin
- ✓ Starts Docker service
- ✓ Configures user permissions
- ✓ Verifies installation

**Important:** You'll need to logout/login after installation for group permissions to take effect.

#### Manual Installation

**Docker Desktop (Windows/Mac):**
1. Download from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Install and start Docker Desktop
3. For WSL2: Enable WSL2 integration in Settings → Resources → WSL Integration

**Docker Engine (Linux):**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# RHEL/Fedora
sudo dnf install docker-ce docker-ce-cli containerd.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

**Verify Docker installation:**
```bash
docker --version        # Should show Docker version 20.10+
docker compose version  # Should show Compose version 2.0+
docker ps              # Should show running containers (or empty table)
```

### Other Requirements

- **Python 3.11+** (for local development)
- **Minimum 4GB RAM** (8GB+ recommended for production)
- **10GB disk space** (for images and data)

## Quick Start (Docker)

### Single Container (Development)

The fastest way to get started:

```bash
# Clone repository
git clone https://github.com/your-org/kosmos.git
cd kosmos

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Build and run
docker build -t kosmos:latest .
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -v $(pwd)/results:/app/results \
  kosmos:latest
```

### Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-11-13T...",
#   "uptime_seconds": 15.2,
#   "service": "kosmos-ai-scientist",
#   "version": "1.0.0"
# }
```

## Production Deployment (Docker Compose)

### Initial Setup

1. **Clone and configure**:

```bash
git clone https://github.com/your-org/kosmos.git
cd kosmos

# Copy and configure environment
cp .env.example .env
```

2. **Edit .env file**:

```bash
# Required: Add your API key
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# Recommended: Use PostgreSQL for production
DATABASE_URL=postgresql://kosmos:kosmos-dev-password@postgres:5432/kosmos

# Enable Redis caching
REDIS_ENABLED=true
REDIS_URL=redis://redis:6379/0

# Enable concurrent operations for performance
ENABLE_CONCURRENT_OPERATIONS=true
MAX_CONCURRENT_EXPERIMENTS=4

# Production logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

3. **Start services**:

```bash
# Start in production mode
docker-compose --profile prod up -d

# View logs
docker-compose logs -f kosmos

# Check service health
docker-compose ps
```

### Service Configuration

#### PostgreSQL Database

The database is configured with:
- **Automatic backups**: Enabled via volumes
- **Health checks**: Every 10 seconds
- **Resource limits**: 2 CPU, 2GB RAM
- **Persistent storage**: `./postgres_data`

#### Redis Cache

Configured for optimal caching:
- **Max memory**: 256MB with LRU eviction
- **Persistence**: AOF + snapshots
- **Health checks**: Every 10 seconds
- **Resource limits**: 1 CPU, 512MB RAM

#### Neo4j Knowledge Graph

Optional graph database for advanced features:
- **Memory**: 1GB heap, 512MB page cache
- **APOC plugins**: Enabled
- **Web UI**: http://localhost:7474
- **Resource limits**: 2 CPU, 2GB RAM

### Managing Services

```bash
# Start all production services
docker-compose --profile prod up -d

# Start development services (includes pgAdmin)
docker-compose --profile dev up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Restart specific service
docker-compose restart kosmos

# View resource usage
docker stats

# Access pgAdmin (dev mode only)
# URL: http://localhost:5050
# Email: admin@kosmos.local
# Password: admin
```

## Kubernetes Deployment

### Quick Deploy

For production-grade Kubernetes deployment:

```bash
# Create namespace
kubectl create namespace kosmos

# Apply configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/neo4j-statefulset.yaml
kubectl apply -f k8s/kosmos-deployment.yaml
kubectl apply -f k8s/kosmos-service.yaml
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get pods -n kosmos
kubectl get services -n kosmos
```

### Prerequisites

1. **Create secrets file** from template:

```bash
# Create k8s/secrets.yaml from template
cp k8s/secrets.yaml.template k8s/secrets.yaml

# Edit and add your actual API key
# Base64 encode: echo -n "sk-ant-..." | base64
```

2. **Configure storage**:

```yaml
# k8s/pv.yaml - Adjust for your storage provider
kind: PersistentVolume
apiVersion: v1
metadata:
  name: postgres-pv
spec:
  capacity:
    storage: 50Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: standard
  hostPath:
    path: /mnt/data/postgres
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment kosmos --replicas=3 -n kosmos

# Enable auto-scaling
kubectl apply -f k8s/hpa.yaml

# Monitor scaling
kubectl get hpa -n kosmos
```

### Service Mesh (Optional)

For advanced traffic management with Istio:

```bash
# Install Istio
istioctl install --set profile=production

# Enable sidecar injection
kubectl label namespace kosmos istio-injection=enabled

# Apply virtual services
kubectl apply -f k8s/istio/virtual-service.yaml
kubectl apply -f k8s/istio/destination-rule.yaml
```

## Cloud Provider Guides

### AWS Deployment

#### ECS Fargate

```bash
# Install AWS CLI
aws configure

# Create ECS cluster
aws ecs create-cluster --cluster-name kosmos-prod

# Create task definition
aws ecs register-task-definition --cli-input-json file://aws/task-definition.json

# Create service
aws ecs create-service \
  --cluster kosmos-prod \
  --service-name kosmos \
  --task-definition kosmos:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

#### RDS PostgreSQL

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier kosmos-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.4 \
  --master-username kosmos \
  --master-user-password <password> \
  --allocated-storage 100 \
  --storage-type gp3 \
  --vpc-security-group-ids sg-xxx \
  --db-subnet-group-name kosmos-subnet-group \
  --backup-retention-period 7 \
  --multi-az

# Get endpoint
aws rds describe-db-instances --db-instance-identifier kosmos-db
```

#### ElastiCache Redis

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id kosmos-cache \
  --cache-node-type cache.t3.medium \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --security-group-ids sg-xxx \
  --cache-subnet-group-name kosmos-cache-subnet
```

### GCP Deployment

#### GKE (Google Kubernetes Engine)

```bash
# Create GKE cluster
gcloud container clusters create kosmos-prod \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-4 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10 \
  --enable-autorepair \
  --enable-autoupgrade

# Get credentials
gcloud container clusters get-credentials kosmos-prod --zone us-central1-a

# Deploy using kubectl
kubectl apply -f k8s/
```

#### Cloud SQL PostgreSQL

```bash
# Create Cloud SQL instance
gcloud sql instances create kosmos-db \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-8192 \
  --region=us-central1 \
  --backup \
  --enable-bin-log \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=02

# Create database
gcloud sql databases create kosmos --instance=kosmos-db

# Create user
gcloud sql users create kosmos \
  --instance=kosmos-db \
  --password=<secure-password>
```

#### Memorystore Redis

```bash
# Create Redis instance
gcloud redis instances create kosmos-cache \
  --size=2 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

### Azure Deployment

#### AKS (Azure Kubernetes Service)

```bash
# Create resource group
az group create --name kosmos-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group kosmos-rg \
  --name kosmos-aks \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 10 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group kosmos-rg --name kosmos-aks

# Deploy
kubectl apply -f k8s/
```

#### Azure Database for PostgreSQL

```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group kosmos-rg \
  --name kosmos-db \
  --location eastus \
  --admin-user kosmos \
  --admin-password <secure-password> \
  --sku-name Standard_D4s_v3 \
  --tier GeneralPurpose \
  --version 15 \
  --storage-size 128 \
  --backup-retention 7 \
  --high-availability Enabled
```

#### Azure Cache for Redis

```bash
# Create Redis cache
az redis create \
  --resource-group kosmos-rg \
  --name kosmos-cache \
  --location eastus \
  --sku Standard \
  --vm-size c2
```

## Monitoring & Observability

### Prometheus Metrics

1. **Install Prometheus**:

```bash
# Using Docker
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Or Kubernetes
kubectl apply -f k8s/monitoring/prometheus.yaml
```

2. **Configure scraping**:

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kosmos'
    static_configs:
      - targets: ['kosmos:8000']
    metrics_path: '/metrics'
```

3. **Available metrics**:

- `kosmos_research_cycles_total` - Total research cycles
- `kosmos_experiments_total` - Total experiments
- `kosmos_api_calls_total` - API call count
- `kosmos_api_cost_usd_total` - Cumulative API costs
- `kosmos_cache_hit_ratio` - Cache effectiveness
- `kosmos_experiment_duration_seconds` - Experiment timing
- See full list in `kosmos/monitoring/metrics.py`

### Grafana Dashboards

1. **Install Grafana**:

```bash
# Using Docker
docker run -d \
  --name=grafana \
  -p 3000:3000 \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  grafana/grafana

# Access: http://localhost:3000
# Default credentials: admin/admin
```

2. **Add Prometheus data source**:
   - Navigate to Configuration > Data Sources
   - Add Prometheus: http://prometheus:9090

3. **Import dashboards**:
   - Research Workflow: `monitoring/grafana/research-dashboard.json`
   - System Health: `monitoring/grafana/health-dashboard.json`
   - Cost Tracking: `monitoring/grafana/cost-dashboard.json`

### Logging

#### Centralized Logging with ELK Stack

```bash
# Start ELK stack
docker-compose -f docker-compose.elk.yml up -d

# Configure Filebeat to ship Kosmos logs
# monitoring/filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /app/logs/*.log
    json.keys_under_root: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

#### Loki + Grafana (Lightweight)

```bash
# Add Loki to docker-compose.yml
loki:
  image: grafana/loki:latest
  ports:
    - "3100:3100"
  volumes:
    - ./monitoring/loki-config.yml:/etc/loki/local-config.yaml

promtail:
  image: grafana/promtail:latest
  volumes:
    - ./logs:/var/log
    - ./monitoring/promtail-config.yml:/etc/promtail/config.yml
```

### Health Checks

Monitor service health:

```bash
# Basic health (liveness)
curl http://localhost:8000/health

# Readiness check (dependencies)
curl http://localhost:8000/health/ready

# System metrics
curl http://localhost:8000/health/metrics
```

### Alerts

Configure alerting in `kosmos/monitoring/alerts.py`:

```python
# Email alerts
export ALERT_EMAIL_ENABLED=true
export ALERT_EMAIL_TO=ops@example.com
export SMTP_HOST=smtp.gmail.com
export SMTP_USER=alerts@example.com
export SMTP_PASSWORD=<app-password>

# Slack alerts
export ALERT_SLACK_ENABLED=true
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# PagerDuty (critical only)
export ALERT_PAGERDUTY_ENABLED=true
export PAGERDUTY_INTEGRATION_KEY=<your-key>
```

## Security

### API Key Management

**Never commit API keys to version control!**

1. **Use environment variables**:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

2. **Use secrets management**:

```bash
# Kubernetes secrets
kubectl create secret generic kosmos-secrets \
  --from-literal=anthropic-api-key=sk-ant-... \
  -n kosmos

# AWS Secrets Manager
aws secretsmanager create-secret \
  --name kosmos/anthropic-api-key \
  --secret-string "sk-ant-..."

# GCP Secret Manager
echo -n "sk-ant-..." | gcloud secrets create anthropic-api-key --data-file=-
```

3. **Rotate keys regularly**:

```bash
# Update secret
kubectl edit secret kosmos-secrets -n kosmos

# Restart pods to pick up new secret
kubectl rollout restart deployment/kosmos -n kosmos
```

### Network Security

1. **TLS/SSL encryption**:

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kosmos-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - kosmos.yourdomain.com
      secretName: kosmos-tls
  rules:
    - host: kosmos.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: kosmos
                port:
                  number: 8000
```

2. **Network policies**:

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: kosmos-netpol
  namespace: kosmos
spec:
  podSelector:
    matchLabels:
      app: kosmos
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: nginx-ingress
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
```

### Security Scanning

```bash
# Scan Docker image for vulnerabilities
docker scan kosmos:latest

# Using Trivy
trivy image kosmos:latest

# Scan Kubernetes manifests
kubesec scan k8s/kosmos-deployment.yaml

# Check for misconfigurations
checkov -d k8s/
```

## Scaling

### Horizontal Pod Autoscaling (HPA)

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: kosmos-hpa
  namespace: kosmos
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: kosmos
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: kosmos_experiments_active
        target:
          type: AverageValue
          averageValue: "5"
```

### Database Scaling

#### PostgreSQL Read Replicas

```bash
# AWS RDS
aws rds create-db-instance-read-replica \
  --db-instance-identifier kosmos-db-replica-1 \
  --source-db-instance-identifier kosmos-db \
  --db-instance-class db.t3.medium

# Configure read/write split in application
export DATABASE_WRITE_URL=postgresql://kosmos:pass@primary:5432/kosmos
export DATABASE_READ_URL=postgresql://kosmos:pass@replica:5432/kosmos
```

#### Redis Cluster

```bash
# Redis Cluster mode
redis-cli --cluster create \
  node1:6379 node2:6379 node3:6379 \
  node4:6379 node5:6379 node6:6379 \
  --cluster-replicas 1
```

### Rate Limiting

Configure in `.env`:

```bash
# API rate limits
LLM_RATE_LIMIT_PER_MINUTE=100
MAX_CONCURRENT_LLM_CALLS=10

# Experiment parallelism
MAX_CONCURRENT_EXPERIMENTS=8
MAX_PARALLEL_HYPOTHESES=5
```

## Backup & Disaster Recovery

### Database Backups

#### Automated PostgreSQL Backups

```bash
# Create backup script
cat > backup-postgres.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups
docker exec kosmos-postgres pg_dump -U kosmos kosmos | gzip > $BACKUP_DIR/kosmos_$DATE.sql.gz
find $BACKUP_DIR -name "kosmos_*.sql.gz" -mtime +7 -delete
EOF

# Schedule with cron
crontab -e
# Add: 0 2 * * * /path/to/backup-postgres.sh
```

#### Cloud-native Backups

```bash
# AWS RDS automated backups (configured during creation)
aws rds modify-db-instance \
  --db-instance-identifier kosmos-db \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00"

# Manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier kosmos-db \
  --db-snapshot-identifier kosmos-manual-$(date +%Y%m%d)
```

### Volume Backups

```bash
# Backup volumes
docker run --rm \
  -v kosmos_postgres_data:/source:ro \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres_$(date +%Y%m%d).tar.gz -C /source .

# Restore
docker run --rm \
  -v kosmos_postgres_data:/target \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/postgres_20241113.tar.gz -C /target
```

### Disaster Recovery Plan

1. **Regular backups**: Daily automated backups
2. **Geo-redundancy**: Multi-region deployment
3. **Recovery procedures**: Documented runbooks
4. **Testing**: Quarterly DR drills
5. **RTO/RPO targets**:
   - Recovery Time Objective: < 1 hour
   - Recovery Point Objective: < 15 minutes

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs
docker-compose logs kosmos

# Check health
docker inspect kosmos-app | grep Health

# Common fixes:
# 1. Check API key is set
env | grep ANTHROPIC_API_KEY

# 2. Check database connectivity
docker-compose exec kosmos python -c "from kosmos.db import get_session; get_session()"

# 3. Check port conflicts
netstat -tuln | grep 8000
```

#### Database Connection Errors

```bash
# Check Postgres is running
docker-compose ps postgres

# Test connection manually
docker-compose exec postgres psql -U kosmos -d kosmos -c "SELECT 1"

# Check connection string
docker-compose exec kosmos env | grep DATABASE_URL

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### High Memory Usage

```bash
# Check memory usage
docker stats

# Adjust limits in docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 2G

# Or in .env:
MAX_CONCURRENT_EXPERIMENTS=2  # Reduce parallelism
```

#### Performance Issues

```bash
# Enable profiling
export ENABLE_PROFILING=true
export PROFILING_MODE=standard

# Check bottlenecks
kosmos profile view

# Optimize database queries
export DATABASE_ECHO=true  # Log slow queries

# Check cache hit rate
curl http://localhost:8000/health/metrics | grep cache_hit_ratio
```

### Debug Mode

```bash
# Run with debug logging
docker-compose exec kosmos kosmos run --debug "Research question"

# Enable SQL query logging
export DATABASE_ECHO=true

# Enable API request logging
export LOG_API_REQUESTS=true
```

## Maintenance

### Update Procedures

#### Rolling Updates (Kubernetes)

```bash
# Update image
kubectl set image deployment/kosmos kosmos=kosmos:v1.1.0 -n kosmos

# Monitor rollout
kubectl rollout status deployment/kosmos -n kosmos

# Rollback if needed
kubectl rollout undo deployment/kosmos -n kosmos
```

#### Zero-Downtime Updates (Docker Compose)

```bash
# Build new image
docker build -t kosmos:v1.1.0 .

# Tag as latest
docker tag kosmos:v1.1.0 kosmos:latest

# Scale up with new version
docker-compose up -d --scale kosmos=2 --no-recreate

# Remove old containers
docker-compose up -d --scale kosmos=1
```

### Database Migrations

```bash
# Run Alembic migrations
docker-compose exec kosmos alembic upgrade head

# Rollback if needed
docker-compose exec kosmos alembic downgrade -1

# Create new migration
docker-compose exec kosmos alembic revision --autogenerate -m "Description"
```

### Dependency Updates

```bash
# Update Python dependencies
docker-compose exec kosmos pip install --upgrade -r requirements.txt

# Rebuild image
docker-compose build kosmos

# Restart with new dependencies
docker-compose up -d kosmos
```

### Log Rotation

Configure in `docker-compose.yml`:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Cleanup

```bash
# Remove old containers
docker system prune -a --volumes

# Clean old logs
find ./logs -name "*.log" -mtime +30 -delete

# Vacuum database
docker-compose exec postgres vacuumdb -U kosmos -d kosmos --analyze --verbose
```

---

## Support

For issues and questions:

- **GitHub Issues**: https://github.com/your-org/kosmos/issues
- **Documentation**: https://docs.kosmos.ai
- **Email**: support@kosmos.ai

## License

See [LICENSE](LICENSE) file for details.
