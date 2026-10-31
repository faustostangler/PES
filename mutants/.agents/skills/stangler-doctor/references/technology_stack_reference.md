# Doctor Stangler SOTA-KISS Technology Stack Reference

> **Status**: Living Reference / Canonical Architectural Baseline  
> **Target Profile**: Principal Socio-Technical Architect (DevOps & DDD Specialist)  
> **Architecture Style**: Microservices-Ready Modular Monolith, Clean & Hexagonal Architecture, 12-Factor App  
> **Language Rule**: Code, specifications, and symbols are strictly in English.

---

## 1. Decision Drivers & Guiding Principles

Every technology selection in this stack and method is governed by four core architectural forces to be used as and when needed to know which technology to use when:

1. **Delivery Velocity & DX (Developer Experience)**: Optimized for high-throughput, low-friction engineering in lean teams. Minimize boilerplate, maximize type safety, eliminate accidental complexity (KISS principle).
2. **End-to-End Contract Generation & Type Safety**: Seamless schema synchronization from backend models (Pydantic V2 / OpenAPI 3.1) to frontend clients (`Orval` -> TypeScript + TanStack Query), making runtime type mismatches impossible.
3. **Maturidade para Visualização de Dados & Dashboards**: First-class capabilities for high-frequency financial time-series (B3), audio spectrograms/waveforms, knowledge graphs, and operational metrics.
4. **Hexagonal Architecture Alignment**: Strict boundary segregation between the pure Domain layer, Application use cases, Infrastructure adapters, and Presentation delivery mechanisms.

---

## 2. Layer-by-Layer Technology Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                              │
│  React 19 (Vite) + TS (Strict) + Tailwind + shadcn/ui + TanStack       │
│  Metabase (Self-Hosted BI) │ Typer + Rich (CLI)                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / OpenAPI Contracts (Orval)
┌───────────────────────────────────▼────────────────────────────────────┐
│                        APPLICATION & API LAYER                         │
│  FastAPI + Uvicorn │ ARQ Workers + Redis │ BackgroundTasks             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Pure Python Ports & Use Cases
┌───────────────────────────────────▼────────────────────────────────────┐
│                              DOMAIN CORE                               │
│  Value Objects + Entities (Pydantic V2 / dataclasses) │ No Frameworks  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Adapters & ACLs
┌───────────────────────────────────▼────────────────────────────────────┐
│                       INFRASTRUCTURE & PERSISTENCE                     │
│  SQLAlchemy 2.0 (asyncpg) + Alembic │ PostgreSQL 16+ (pgvector)        │
│  Polars (Arrow / Parquet / Feather) │ HTTPX + Playwright + Selectolax  │
│  Redis 7+ (Cache, Pub/Sub, Queue)   │ Langfuse + OpenTelemetry         │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Camada 1: Ingestão, Processamento de Dados & Scraping

| Capability | Primary Tool | Fallback / Secondary | Architectural Purpose & Rationale |
| :--- | :--- | :--- | :--- |
| **Tabular Data Processing** | **Polars + Python Async** | **Pandas** | In-memory Rust multithreaded query engine with Apache Arrow memory layout. Handles millions of rows with minimal RAM footprint and lazy evaluation. Pandas is retained only when interfacing with legacy libraries lacking Arrow support. |
| **Distributed Task Queue** | **ARQ + Redis** | **FastAPI BackgroundTasks** | Native async Redis job queue with minimal overhead. Replaces heavyweight Celery for background workers, scraping queues, and batch pipelines. Lightweight jobs use `BackgroundTasks`. |
| **HTTP Client & Requests** | **HTTPX (Async + Sync)** | — | Modern, async-first HTTP/1.1 and HTTP/2 client with connection pooling, timeouts, and full compatibility with FastAPI ASGI loops. |
| **Retry & Resilience** | **Tenacity** | — | Declarative retry strategies (exponential backoff, jitter, specific exception filters) for network and scraper adapters. |
| **HTML/XML Parsing** | **Selectolax** | **BeautifulSoup4** | Ultra-fast HTML parsing powered by C/Rust Modest and Lexbor engines (up to 30x faster than BS4). BS4 is preserved solely for corrupted HTML structures. |
| **Headless Browser Scraping** | **Playwright (Async)** | — | Reliable browser automation with hermetic browser binaries, auto-waiting, network route interception, and dynamic DOM evaluation. |

---

### Camada 2: Banco de Dados, Persistência e Cache

| Capability | Selected Tool | Architectural Purpose & Rationale |
| :--- | :--- | :--- |
| **Relational Database** | **PostgreSQL 16+** | Industry-standard ACID RDBMS with JSONB support, transactional integrity, and strong concurrency control. |
| **Vector Storage (AI & RAG)** | **PostgreSQL + pgvector** | Unified vector search inside PostgreSQL. Eliminates the operational burden of managing a separate vector database for semantic search, embeddings, and RAG. |
| **In-Memory Cache & Broker** | **Redis 7+** | Sub-millisecond caching, rate-limiting, distributed locks, session state, and messaging transport for ARQ. |
| **Async DB Driver** | **asyncpg** | High-performance PostgreSQL async driver for binary protocol execution without blocking the event loop. |
| **ORM & Schema Migrations** | **SQLAlchemy 2.0 (Async) + Alembic** | Used strictly inside `infrastructure/` persistence adapters. Domain entities never inherit from ORM models. Schema migrations are versioned and automated with Alembic. |
| **Zero-Copy Serialization** | **Parquet & Feather (PyArrow IPC)** | Canonical format for offline analytical datasets and high-speed dataframe persistence. Replaces unsafe `.pkl` files. |

---

### Camada 3: Backend, API e Servidor

| Capability | Selected Tool | Architectural Purpose & Rationale |
| :--- | :--- | :--- |
| **Web & API Framework** | **FastAPI + Uvicorn** | Type-safe ASGI application server. Provides high-throughput request handling and auto-generates interactive OpenAPI documentation. |
| **Client Code Generation** | **Orval** | Generates strongly-typed TypeScript clients and TanStack Query hooks directly from the FastAPI OpenAPI schema. |
| **Local Async Tasks** | **BackgroundTasks** | Fires non-blocking asynchronous jobs (e.g., audit logging, notifications) within the API process lifecycle. |
| **Configuration Management** | **pydantic-settings** | Centralized, fail-fast configuration in `config.py` sourced from `.env` files. Crashes at startup if required variables are missing or invalid. |

---

### Camada 4: Frontend & UI

| Capability | Selected Tool | Architectural Purpose & Rationale |
| :--- | :--- | :--- |
| **Framework & Build System** | **React 19 + Vite** | Lightweight, high-velocity frontend architecture with lightning-fast HMR and modular component composition. |
| **Language & Typings** | **TypeScript (Strict Mode)** | End-to-end static type safety preventing runtime errors. |
| **Styling & Design System** | **Tailwind CSS + shadcn/ui** | Accessible, copy-paste headless UI components with complete control over tokens and CSS variables. |
| **Server State & Caching** | **TanStack Query (React Query)** | Manages API fetching, smart caching, deduplication, background polling, and optimistic updates. |
| **Table & Data Grid** | **TanStack Table** | Headless, high-performance table engine for complex sorting, filtering, and pagination of large datasets. |
| **Client State Management** | **Zustand** | Minimalist, boilerplate-free global state store for client-only application state. |

---

### Camada 5: Business Intelligence, Analytics & Visualização

| Capability | Selected Tool | Architectural Purpose & Rationale |
| :--- | :--- | :--- |
| **Self-Hosted BI Platform** | **Metabase (Docker)** | Zero-code/low-code business intelligence, SQL exploration, and automated dashboard creation directly on PostgreSQL. |
| **Interactive Charting** | **Apache ECharts** | Canvas/SVG rendering for complex financial time-series (candlesticks, volume), heatmaps, and audio spectrograms. |
| **Dashboard UI Blocks** | **Tremor** | Pre-built, aesthetically polished analytics cards, KPIs, and metric charts tailored for React + Tailwind. |

---

### Camada 6: Ciência de Dados, IA & Áudio

| Capability | Selected Tool | Architectural Purpose & Rationale |
| :--- | :--- | :--- |
| **Vector & Matrix Math** | **NumPy** | Baseline numerical computing and array manipulation. |
| **Traditional Machine Learning** | **Scikit-learn** | Classification, clustering, regression, and preprocessing pipelines when deep models are unnecessary. |
| **Deep Learning & Neural Networks** | **PyTorch** | Leading ecosystem for deep learning, embeddings generation, transformer fine-tuning, and model inference. |
| **Audio Processing & Analysis** | **Librosa + Essentia** | Audio feature extraction (MFCCs, spectral roll-off, chroma, rhythm, tonal analysis) for music engineering and detranscription pipelines. |

---

### Camada 7: Testes, Qualidade & Validação

| Capability | Selected Tool | Architectural Purpose & Rationale |
| :--- | :--- | :--- |
| **Data Validation** | **Pydantic V2** | Ultra-fast Rust-based runtime data validation for Value Objects and API DTOs. |
| **Test Runner & Harness** | **Pytest + pytest-asyncio + pytest-cov** | Standardized test execution with strict coverage reporting. |
| **Mock Data & Factories** | **Polyfactory** | Dynamic, type-driven fixture generation directly from Pydantic models. |
| **Mutation Testing** | **Mutmut** | Verifies test suite efficacy: 0 surviving mutants required in Domain and Application layers. |
| **API Contract & Fuzzing** | **Schemathesis** | Automated property-based fuzzing against OpenAPI endpoints to catch edge-case crashes. |
| **Linting & Formatting** | **Ruff** | Blazing-fast Rust linter and formatter replacing Black, Flake8, and isort. |
| **Static Type Checking** | **Mypy (`--strict`)** | Strict static type checking to eliminate `None` references and type regressions. |

---

### Camada 8: CLI, Observabilidade & Telemetria

| Capability | Selected Tool | Architectural Purpose & Rationale |
| :--- | :--- | :--- |
| **CLI & Terminal Styling** | **Typer + Rich** | Declarative CLI commands with automatic help generation and rich terminal formatting. |
| **Structured Logging** | **structlog** | JSON-formatted contextual logs carrying trace IDs and correlation context. |
| **Metrics & Tracing** | **OpenTelemetry + Prometheus** | Prometheus Golden Signals (Latency, Traffic, Errors, Saturation) and distributed tracing. |
| **Log Aggregation & Dashboards**| **Grafana + Grafana Loki** | Centralized dashboard visualization and log querying. |
| **Error Tracking** | **Sentry** | Crash reporting with stack traces, environment tags, and LGPD/PII data redaction. |
| **LLM Telemetry & Evals** | **Langfuse** | Clinical observability for generative AI: prompt versioning, generation tracing, and eval scoring (faithfulness, hallucination). |

---

### Camada 9: DevOps, Containerização & Toolchain

| Capability | Selected Tool | Architectural Purpose & Rationale |
| :--- | :--- | :--- |
| **Package & Env Manager** | **uv** | Ultra-fast Rust package manager ensuring deterministic builds via `pyproject.toml` and `uv.lock`. |
| **Containerization** | **Docker (Multi-Stage)** | Single Dockerfile acting as the Single Source of Truth to manifest API, Worker, and CLI roles. |
| **Local Orchestration** | **Docker Compose** | Single declarative manifest provisioning API, Worker, PostgreSQL, Redis, and Metabase. |

---

## 3. Frontend Selection Decision: React vs. Angular

### Why React 19 over Angular:
- **Ecosystem Dominance in Data & Charts**: React hosts the most mature charting ecosystems (Apache ECharts, Visx, Recharts, Tremor) essential for financial and audio analytics.
- **Contract-Driven OpenAPI Workflow**: Orval generates TypeScript interfaces and TanStack Query hooks directly from FastAPI schemas with zero manual mapping.
- **Lightweight State Architecture**: Zustand + TanStack Query decouples server state from client state without RxJS stream overhead.
- **Hexagonal Architecture Compatibility**: Allows clean isolation between UI views, application hooks, and API adapters without framework-enforced service decorators.

---

## 4. Canonical Project Directory Structure Reference

```
my-project/
├── pyproject.toml              # Managed via uv (deterministic builds)
├── uv.lock                     # Locked dependency tree
├── Dockerfile                  # Single multi-target Dockerfile
├── docker-compose.yml          # Postgres + Redis + API + Worker + Metabase
├── src/
│   ├── config.py               # pydantic-settings (Fail-Fast configuration)
│   ├── domain/                 # Pure Python: Value Objects, Entities, Invariants
│   │   ├── exceptions.py
│   │   ├── value_objects.py    # Strong types (ContentId, Ticker, etc.)
│   │   └── entities.py         # Business entities enforcing invariants at __init__
│   ├── application/            # Use Cases & Abstract Ports (ABCs)
│   │   ├── ports/              # Repository & service interfaces
│   │   └── use_cases/          # Business workflow orchestration
│   ├── infrastructure/         # External Adapters & I/O implementations
│   │   ├── database/           # SQLAlchemy 2.0 ORM models & Postgres adapters
│   │   ├── scrapers/           # HTTPX, Playwright & Selectolax adapters
│   │   └── telemetry/          # structlog, Prometheus, Sentry, Langfuse
│   └── presentation/           # Delivery Mechanisms (Humble Object Pattern)
│       ├── api/                # FastAPI routers & request/response schemas
│       └── cli/                # Typer commands with Rich formatting
└── frontend/                   # React 19 SPA
    ├── src/
    │   ├── api/                # Auto-generated via Orval from backend openapi.json
    │   ├── components/         # shadcn/ui + Tremor + Tailwind CSS
    │   ├── hooks/              # Custom TanStack Query & Zustand hooks
    │   └── views/              # Pages & interactive dashboards
    ├── package.json
    └── vite.config.ts
```
