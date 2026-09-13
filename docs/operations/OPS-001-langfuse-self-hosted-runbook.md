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
┌────────────────────────────────────────────────────────┐
│ Host Machine (:3000)                                   │
│                                                        │
│  ┌─────────────────────────┐   ┌────────────────────┐  │
│  │ cresmo-langfuse-server  │──▶│ cresmo-langfuse-db │  │
│  │ (langfuse/langfuse:2)   │   │ (postgres:16)      │  │
│  └─────────────────────────┘   └────────────────────┘  │
│               │                           │            │
└───────────────┼───────────────────────────┼────────────┘
                ▼                           ▼
        HTTP Web UI / API           Named Docker Volume
      (http://localhost:3000)   (cresmo_langfuse_postgres_data)
```

### Container Services
- **`cresmo-langfuse-server`**: Langfuse v2 web application and REST/OTLP ingestion API listening on `0.0.0.0:3000`.
- **`cresmo-langfuse-db`**: PostgreSQL 16 Alpine instance with automated healthcheck (`pg_isready`).
- **`cresmo_langfuse_postgres_data`**: Named volume guaranteeing data persistence across container recycles.

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

## 5. Application Configuration (`.env`)

Add the extracted credentials into your root `.env` file (`.env`):

```bash
# ==========================================
# Langfuse LLM Observability & Telemetry (Self-Hosted)
# ==========================================
LANGFUSE_PUBLIC_KEY="pk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
LANGFUSE_SECRET_KEY="sk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
LANGFUSE_HOST="http://localhost:3000"
```

The application's `CresmoSettings` fail-fast configuration validator automatically verifies these variables and binds them into `GeminiLLMAdapter` and the `@observe` decorator context.

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
