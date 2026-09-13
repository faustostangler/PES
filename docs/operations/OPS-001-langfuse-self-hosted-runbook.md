# OPS-001: Self-Hosted Langfuse Observability Runbook

**Context**: Cresmo Knowledge Synthesis Engine  
**Domain**: Platform & SRE Observability  
**Status**: APPROVED OPERATIONAL RUNBOOK  
**Governing ADRs**: [`ADR-001`](../adr/ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-003`](../adr/ADR-003-pes-production-architecture.md)  
**Governing Spec**: [`EVAL-001`](../specs/EVAL-001-cresmo-synthesis.md)  
**Stack Definition**: [`docker-compose.langfuse.yml`](../../docker-compose.langfuse.yml)

---

## 1. Overview & Architectural Purpose

In accordance with [`ADR-001`](../adr/ADR-001-cresmo-modular-monolith-strangling.md) and [`EVAL-001`](../specs/EVAL-001-cresmo-synthesis.md), the Cresmo engine enforces mandatory AI telemetry across all generative LLM calls (`LLMTransformationPort`). 

While Langfuse Cloud imposes monthly quota limits (50k observations/month) and short retention windows (30 days), this **Self-Hosted Docker deployment** provides:
- **Zero quota limits**: Unlimited generation spans, traces, and latency evaluations.
- **Permanent retention**: Historical trace and token metrics stored indefinitely in local persistent volumes.
- **Data sovereignty**: All prompt payloads and synthesized knowledge remain 100% on the local host.

---

## 2. Infrastructure Topology

The self-hosted stack is defined as immutable Infrastructure-as-Code in `docker-compose.langfuse.yml`:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ Host Machine (:3000)                                                                    │
│                                                                                         │
│  ┌────────────────────────┐      ┌─────────────────────────┐     ┌───────────────────┐  │
│  │  cresmo-langfuse-db    │◀─────│ cresmo-langfuse-server  │────▶│ cresmo-clickhouse │  │
│  │     (postgres:16)      │      │   (langfuse/langfuse:3) │     │ (clickhouse:24.3) │  │
│  └────────────────────────┘      └─────────────────────────┘     └───────────────────┘  │
│               │                               │                            │            │
│               │                  ┌────────────┴────────────┐               │            │
│               │                  ▼                         ▼               │            │
│               │       ┌──────────────────────┐  ┌──────────────────────┐   │            │
│               │       │ cresmo-langfuse-minio│  │ cresmo-langfuse-redis│   │            │
│               │       │ (chainguard/minio)   │  │   (redis:7-alpine)   │   │            │
│               │       └──────────────────────┘  └──────────────────────┘   │            │
│               │                                                            │            │
└───────────────┼────────────────────────────────────────────────────────────┼────────────┘
                ▼                                                            ▼
      Postgres Volume                                                ClickHouse Volume
(cresmo_langfuse_postgres_data)                               (cresmo_langfuse_clickhouse_data)
```

### Container Services
- **`cresmo-langfuse-server`**: Langfuse v3 web application and native OpenTelemetry OTLP ingestion API (`/api/public/otel/v1/traces`) listening on `0.0.0.0:3000`.
- **`cresmo-langfuse-clickhouse`**: ClickHouse 24.3 columnar database for high-throughput OpenTelemetry trace storage.
- **`cresmo-langfuse-db`**: PostgreSQL 16 Alpine instance managing user accounts, projects, API keys, and relational metadata.
- **`cresmo-langfuse-redis`**: Redis 7 Alpine caching layer and task queue.
- **`cresmo-langfuse-minio`**: Chainguard MinIO S3-compatible blob storage for raw payload events.
- **Persistent Volumes**: `cresmo_langfuse_postgres_data`, `cresmo_langfuse_clickhouse_data`, `cresmo_langfuse_redis_data`, `cresmo_langfuse_minio_data`.


---

## 3. Operational Lifecycle

### 3.1 Starting the Stack
To launch the stack in the background:
```bash
docker compose -f docker-compose.langfuse.yml up -d
```

### 3.2 Checking Health and Status
```bash
docker compose -f docker-compose.langfuse.yml ps
```
Both `cresmo-langfuse-db` and `cresmo-langfuse-server` should report status `Up` (healthy).

### 3.3 Viewing Container Logs
```bash
# Follow logs in real time
docker compose -f docker-compose.langfuse.yml logs -f langfuse-server
```

### 3.4 Stopping the Stack
```bash
# Graceful stop without data loss
docker compose -f docker-compose.langfuse.yml down
```

---

## 4. Initial Setup & Credential Extraction

1. **Access Dashboard**:
   Open your browser and navigate to:
   ```text
   http://localhost:3000
   ```
2. **Account Creation**:
   Register a new account (e.g., `admin@local`). The first account created on a fresh instance is automatically provisioned with Organization Admin privileges.
3. **Project Initialization**:
   Create a project named **`cresmo`**.
4. **Key Generation**:
   - Navigate to **Settings** $\rightarrow$ **API Keys**.
   - Click **Create new API keys**.
   - Copy the generated `Public Key` (`pk-lf-...`) and `Secret Key` (`sk-lf-...`).

---

## 5. Secrets Management & Governance

Under **12-Factor App** principles and **DevOps / SRE** best practices, credentials must be strictly segregated by their consumer domain (Machine vs. Human):

### 5.1 Machine-to-Machine Credentials (API Keys)
- **What they are**: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`.
- **Primary Storage**: Local `.env` file in the project root.
- **Security Guarantee**: The `.env` file is strictly ignored in `.gitignore`.
- **Validation**: Loaded and validated fail-fast by Pydantic V2 (`pydantic-settings`) via `CresmoSettings`, with sensitive tokens masked using `SecretStr`.

```bash
# ==========================================
# Machine-to-Machine AI Telemetry Credentials (.env)
# ==========================================
LANGFUSE_PUBLIC_KEY="pk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
LANGFUSE_SECRET_KEY="sk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
LANGFUSE_HOST="http://localhost:3000"
```

### 5.2 Human Operator Credentials (Web UI User & Password)
- **What they are**: The email and master password used to access the Langfuse administration dashboard (`http://localhost:3000`).
- **Where to Store**:
  1. **Option A (Recommended for Single-Developer Workstations)**: In the root `.env` file as operational variables. Because `.env` is already gitignored and the Single Source of Truth for local environment variables:
     ```bash
     # ==========================================
     # Cresmo Project Human Operator UI Credentials (Self-Hosted Only)
     # ==========================================
     LANGFUSE_ADMIN_EMAIL="admin@cresmo.local"
     LANGFUSE_ADMIN_PASSWORD="<your_secure_master_password>"
     ```
  2. **Option B (Recommended for Team / Multi-Workstation Setups)**: An encrypted **Password Manager** (1Password, Bitwarden, or KeePassXC) under an entry named `Cresmo - Langfuse Local Admin`. This prevents plaintext password sprawl on disk and enables biometric/master-key protection.
  3. **Option C (Production / Enterprise Environments)**: Enterprise Single Sign-On (SSO / OAuth2 / OIDC) integrated directly with GitHub, Google Workspace, or Okta (configured via `NEXTAUTH_URL` and provider environment variables in `docker-compose.langfuse.yml`).

---

## 6. Maintenance & Backup

### 6.1 Database Backup
To take a snapshot of the telemetry database:
```bash
docker compose -f docker-compose.langfuse.yml exec -T langfuse-db \
  pg_dump -U langfuse langfuse > backup_langfuse_$(date +%Y%m%d).sql
```

### 6.2 Database Restoration
```bash
cat backup_langfuse_YYYYMMDD.sql | docker compose -f docker-compose.langfuse.yml exec -T langfuse-db \
  psql -U langfuse -d langfuse
```

### 6.3 Volume Purge (Clean Slate / Reset)
> [!CAUTION]
> This command permanently deletes all traces and telemetry history!
```bash
docker compose -f docker-compose.langfuse.yml down -v
```

### 6.4 Emergency Admin Password Reset (Zero Data Loss)
If you ever forget the web administrator password, you can reset it instantly by running an update directly in PostgreSQL inside the Docker container:

```bash
# Replace 'YOUR_NEW_PASSWORD' and 'YOUR_EMAIL'
docker compose -f docker-compose.langfuse.yml exec -T langfuse-db \
  psql -U langfuse -d langfuse -c "
    UPDATE users 
    SET password = crypt('YOUR_NEW_PASSWORD', gen_salt('bf')) 
    WHERE email = 'YOUR_EMAIL';
  "
```
Once executed, you can immediately log in at `http://localhost:3000` with the new password, keeping all your project traces, spans, and API keys 100% intact.
