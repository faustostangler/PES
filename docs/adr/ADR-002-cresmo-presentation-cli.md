# ADR-002: Cresmo Production CLI Entrypoint and Presentation Layer Orchestration

**Status:** APPROVED  
**Date:** 2026-09-10  
**Decision Makers:** Lead Architect (Fausto Stangler), Stereoscopist (Doctor Stangler Committee)  

---

## 1. Context

Following the architecture established in [`ADR-001: Strangling Cresmo into Hexagonal Modular Monolith`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/docs/adr/ADR-001-cresmo-modular-monolith-strangling.md), the core knowledge synthesis engine resides cleanly in `src/cresmo/` (`domain/`, `application/`, `infrastructure/`). The engine orchestrates the 6 incremental synthesis stages with pure descriptive naming, 100% domain branch coverage, and frozen Langfuse Eval verification.

However, the modular monolith requires an official **Presentation Layer** for operational consumption:
1. **Absence of a Production CLI**: Operators and automated pipelines require a dedicated, decoupled command-line interface that isolates argument parsing, process control, and terminal formatting from the core orchestration engine, eliminating monolithic execution models that conflate runtime configuration, file writes, and LLM execution.
2. **Missing Composition Root**: Production adapters (`NativeMediaIngestionAdapter`, `GeminiLLMAdapter`, `ObsidianVaultAdapter`) need a centralized, deterministic wiring mechanism driven by [`CresmoSettings`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/infrastructure/config.py).
3. **Persistent Idempotency Ledger**: While [`LedgerRepositoryPort`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/application/ports.py) defines the contract for idempotency tracking, only `InMemoryLedgerAdapter` is currently implemented in `src/cresmo/infrastructure/adapters/mock_adapters.py`. Production execution requires a persistent, atomic `JsonLedgerAdapter` compatible with `processed_cresmo.json`.
4. **Standardized Process Control**: Production orchestration (cron jobs, shell runners, CI/CD) requires strict, well-defined CLI exit codes separating configuration errors, domain invariant rejections, API rate limits, and ingestion failures.

Ubiquitous Language definitions are documented in [`CONTEXT.md`](../../CONTEXT.md) and [`docs/GLOSSARY.md`](../GLOSSARY.md).

---

## 2. Decision

We will implement the Presentation Layer in `src/cresmo/presentation/` adhering to the **Humble Object Pattern**, driven by standard library `argparse` and supported by an atomic `JsonLedgerAdapter` in `src/cresmo/infrastructure/adapters/`:

1. **Humble Object CLI Controller (`src/cresmo/presentation/cli.py`)**:
   - Strips all business logic and orchestration from the presentation layer.
   - Implements subcommands:
     - `cresmo run --url <video_url>`: Executes the end-to-end synthesis pipeline for a single target video.
     - `cresmo check-config`: Validates environment settings (`.env`), API keys, and vault paths fail-fast without executing transformations.
   - Accepts operational overrides via CLI flags (`--batch-size`, `--passes`, `--dry-run`).
   - Uses Python's built-in `argparse` to eliminate extra external framework dependencies.

2. **Centralized Composition Root (`src/cresmo/presentation/composition.py`)**:
   - Acts as the pure Dependency Injection assembly root.
   - Reads validated configuration from `CresmoSettings()`.
   - Instantiates production adapters:
     - `NativeMediaIngestionAdapter` as `MediaIngestionPort`.
     - `GeminiLLMAdapter` as `LLMTransformationPort`.
     - `ObsidianVaultAdapter` as `VaultRepositoryPort`.
     - `JsonLedgerAdapter` as `LedgerRepositoryPort`.
   - Injects dependencies into `CresmoPipeline` and returns the ready-to-execute orchestrator.

3. **Atomic File-Based Ledger Adapter (`src/cresmo/infrastructure/adapters/json_ledger_adapter.py`)**:
   - Implements `LedgerRepositoryPort`.
   - Persists completed `ContentId`s in `processed_cresmo.json` (or path configured in `CresmoSettings`).
   - Enforces atomic writes via `{target}.tmp.{uuid4()}` and `os.replace` to prevent file corruption during sudden crashes or SIGINT.

4. **Standardized CLI Exit Code Taxonomy**:
   - `0`: **Success** — Pipeline finished cleanly, notes and MOCs created or video already marked processed.
   - `1`: **Unexpected Internal Error** — Unhandled exception.
   - `2`: **Configuration / CLI Usage Error** — Missing mandatory arguments, invalid flags, or `pydantic.ValidationError` in `CresmoSettings`.
   - `3`: **Domain Invariant / Validation Error** — `DomainValidationError`, `CompendiumStructureError`, `TypologyViolationError`.
   - `4`: **Rate Limit / Quota Exceeded** — `RateLimitExceededError` (HTTP 429 from YouTube or Google Gemini API exhausted).
   - `5`: **Ingestion / Network Error** — `IngestionNetworkError` (download or Whisper transcription failure).

5. **Packaging Entrypoint (`pyproject.toml`)**:
   - Register the console script:
     ```toml
     [project.scripts]
     cresmo = "cresmo.presentation.cli:main"
     ```
   - Enables execution via `uv run cresmo run --url <url>` or direct binary execution when packaged.

---

## 3. Consequences

### Positive
- **Architectural Cohesion**: Hexagonal separation remains intact; the CLI is a humble translator with zero domain logic.
- **Fail-Fast Ergonomics**: Operators can run `cresmo check-config` to verify setup before initiating expensive LLM jobs.
- **Zero New Dependencies**: `argparse` is standard library; avoids adding `click` or `typer` to `pyproject.toml`.
- **Atomic Idempotency**: `JsonLedgerAdapter` guarantees no duplicate processing and cannot corrupt the ledger file on failure.
- **Deterministic Observability**: Exit codes enable unambiguous automation in cron scripts and container orchestration.

### Negative
- `argparse` requires slightly more boilerplate code than decorator-based libraries like `typer`.
- Terminal color formatting is restricted to ANSI escapes or standard stdout to avoid heavy UI dependencies.

### Neutral
- Existing unit tests for `src/cresmo/` remain completely untouched and valid.

---

## 4. Alternatives Considered

### Alternative A: Using `click` or `typer`
- **Pros**: Automatic help generation, type hints for arguments, shell auto-completion.
- **Cons**: Requires adding new dependencies (`click` or `typer`) to `pyproject.toml`, increasing lockfile surface.
- **Why rejected**: Standard library `argparse` fulfills 100% of our Humble Object requirements without bloating the project dependencies.

### Alternative B: Root-level procedural script (`run_cresmo.py`)
- **Pros**: Quick to write in 20 lines.
- **Cons**: Bypasses the presentation layer, encourages mixing environment variables and script logic, and breaks the Modular Monolith standard project layout.
- **Why rejected**: Violates the Clean Architecture Humble Object presentation pattern, coupling presentation concerns with execution runtime and introducing unmanaged script sprawl.

---

## 5. Domain Model Impact

- **Domain Core (`src/cresmo/domain/`)**: **Zero changes**. Sacred, framework-free, and isolated.
- **Application Layer (`src/cresmo/application/`)**: **Zero changes**. `CresmoPipeline` and all use cases remain identical.
- **Infrastructure Layer (`src/cresmo/infrastructure/`)**:
  - Add `src/cresmo/infrastructure/adapters/json_ledger_adapter.py` implementing `LedgerRepositoryPort`.
  - Add `ledger_path: Path` to `CresmoSettings` in `config.py` with default `processed_cresmo.json`.
- **Presentation Layer (`src/cresmo/presentation/`)**:
  - Add `src/cresmo/presentation/__init__.py`.
  - Add `src/cresmo/presentation/composition.py` (Composition Root).
  - Add `src/cresmo/presentation/cli.py` (Humble Object CLI).

---

## 6. Compliance Checklist

- [x] Hexagonal Architecture layers respected (`presentation/` -> `application/` -> `domain/` <- `infrastructure/`)
- [x] Zero business logic in Presentation layer (Humble Object Pattern)
- [x] No framework dependencies added to Domain or Application layers
- [x] Test strategy defined (hermetic unit tests for CLI argument parsing and composition root with mock ports)
- [x] Fail-fast configuration validation via Pydantic Settings V2
- [x] Exit codes standardized and deterministic
- [x] Idempotency persisted atomically

---

## 8. Prescribed Architectural Patterns Catalog

The following design patterns constitute the foundational engineering standards of the Cresmo codebase:

### 8.1 Single Responsibility Principle (SRP - Resposta a um Único Ator)
*   **Principle**: A module or class has one, and only one, reason to change — answering to a single business stakeholder or operational actor.
*   **Application in Cresmo**:
    *   `cli.py`: Solely converts string CLI arguments into structured execution objects.
    *   `run.py`: Translates application results into console formatting and terminal exit codes.
    *   `pipeline.py`: Orchestrates cognitive synthesis stages; completely unaware of terminal or HTTP contexts.
    *   `config.py`: Exclusively parses, validates, and freezes environment configuration.

### 8.2 Don't Repeat Yourself (DRY & Single Source of Truth)
*   **Principle**: Every piece of knowledge, invariant, or business logic must have a single, unambiguous, authoritative representation within the system.
*   **Application in Cresmo**:
    *   Configuration instantiated once at the composition root and injected downward.
    *   Shared synthesis workflows unified via Template Method (`_synthesize_transcript`).
    *   Validation rules centralized in Pydantic models and Value Objects, never duplicated across CLI parsers.

### 8.3 Humble Object Pattern
*   **Principle**: Separating hard-to-test presentation logic (e.g., terminal argument parsing, stdout writes) from business orchestration, leaving the presentation controller as a "humble" coordinator with zero business decisions.
*   **Application in Cresmo**:
    *   `cli.py` and `run.py` perform trivial translation and delegate 100% of domain processing to `CresmoPipeline` and use cases.

### 8.4 Composition Root (Factory Method & Pure Dependency Injection)
*   **Principle**: A single, centralized location in the application where the dependency graph is composed and wired together at startup, before business execution begins.
*   **Application in Cresmo**:
    *   `composition.py` (`build_pipeline`, `build_discover_batch_sources_use_case`, `build_preflight_checker`) resolves settings, wires production adapters (Gemini, SQLite, Obsidian, Native Media), and delivers fully assembled orchestrators.

### 8.5 Fail-Fast & Environmental Preflight Validation
*   **Principle**: Verify all environmental prerequisites (storage write permissions, binary dependencies like `ffmpeg`, and valid API secrets) within milliseconds at startup, aborting cleanly before incurring I/O, download, or inference costs.
*   **Application in Cresmo**:
    *   `PreflightHealthChecker` and Pydantic Settings validation run before pipeline execution.

### 8.6 Template Method Pattern (GoF)
*   **Principle**: Defines the invariant skeleton of an algorithm in an orchestrating method, deferring or isolating specialized pre-processing steps.
*   **Application in Cresmo**:
    *   `pipeline.py` maintains `run_for_video` and `run_for_text_file` as ingestion hooks that delegate to the invariant multi-stage template `_synthesize_transcript`.

### 8.7 Modelagem SOTA de Classes: Tradicional vs. `@dataclass` vs. Pydantic V2
Para erradicar o "cerimonial de boilerplate" (`self.x = x`) sem comprometer a integridade de domínio ou performance, a taxonomia canônica do Cresmo é estritamente segregada por camada e responsabilidade:

1. **Python Tradicional (`class` com `__init__` explícito)**:
   *   **Onde usar**: Orquestradores da Camada de Aplicação (`CresmoPipeline`, `DiscoverBatchSourcesUseCase`, `SynthesizeAtomicBatchUseCase`), Adaptadores de Infraestrutura com estado/recursos gerenciados (`SqliteLedgerAdapter`, `GeminiLLMAdapter`), e Comandos da Camada de Apresentação (`RunCommand`).
   *   **Por quê**: Classes de orquestração representam **comportamento e serviços**, não estruturas de dados passivas. O `__init__` tradicional é indispensável quando há injeção de dependência com fallbacks lazy (ex.: `prompt_provider = prompt_provider or JsonPromptProvider()`), pré-cálculo de parâmetros operacionais (`batch_size = max(1, batch_size)`), ou instanciação de recursos que não devem ser serializáveis ou comparáveis como dados (`__eq__`, `__repr__`).
   *   **Anti-pattern evitado**: Tratar serviços como registros de dados (`@dataclass` em serviços cria `__repr__` pesados e comportamentos de comparação espúrios entre instâncias de adaptadores).

2. **Standard Library `@dataclass` (Nativo do Python)**:
   *   **Onde usar**:
       *   *Value Objects e Entidades Puras de Domínio*: `@dataclass(frozen=True)` com validação de invariantes estrita no `__post_init__` (`ContentId`, `NoteTitle`, `RawTranscript`, `EnrichedCompendium`, `AtomicNote`, `MapOfContent`).
       *   *Objetos de Transporte de Dados (DTOs) e Consultas de Aplicação*: `@dataclass(frozen=True)` para structs imutáveis em memória (`BatchSource`, `BatchDiscoveryQuery`, `DuplicateCluster`, `DeduplicationReport`, `PipelineResult`).
   *   **Por quê**: Elimina 100% do boilerplate cerimonial (`self.x = x`), garante imutabilidade profunda (`frozen=True`), otimiza performance de hashing e igualdade (`__hash__`, `__eq__`), e preserva a regra áurea do DDD de que a camada de Domínio deve permanecer pura, com **zero dependências de frameworks externos**.

3. **Pydantic V2 (`BaseModel` / `pydantic-settings`)**:
   *   **Onde usar**:
       *   *Fronteira Externa de Configuração*: `CresmoSettings(BaseSettings)` em `src/cresmo/infrastructure/config.py`.
       *   *Fronteiras de I/O e Serialização Não Confiável (Anti-Corruption Layer - ACL)*: Parsing de payloads JSON externos não confiáveis vindos de APIs LLM (`extract_json_data`), validação de esquemas OpenAPI ou requisições HTTP caso exposto via API Web.
   *   **Por quê**: O Pydantic V2 (em Rust) oferece coerção automática de tipos, fail-fast em variáveis de ambiente, mascaramento de segredos (`SecretStr`), e parsing resiliente de strings JSON.
   *   **Regra de ouro**: O Pydantic protege as fronteiras externas (I/O, Config, Schemas de LLM). O `@dataclass(frozen=True)` protege o coração sagrado e imutável do Domínio (`src/cresmo/domain/`).

### 8.8 Ordered Unique Queue / Deduplicated Sequence (Deduplicação $O(1)$ com Ordem Preservada)
*   **Principle**: Em algoritmos de ingestão, varredura de diretórios ou orquestração de filas em que é mandatório desduplicar elementos preservando simultaneamente a ordem determinística de despacho (FIFO), combina-se uma tabela hash (`set[T]`) para validação de pertinência em tempo constante $O(1)$ com uma sequência linear (`list[T]`) para agendamento ordenado.
*   **Application in Cresmo**:
    *   `DiscoverBatchSourcesUseCase._classify_seeds`: utiliza `probed_channels: set[str]` para checagem $O(1)$ instantânea e `channels_to_probe: list[str]` para despacho ordenado de varredura. Evita degradação quadrática $O(N^2)$ em lagos com milhares de arquivos locais.

### 8.9 Explaining Variable on I/O Boundaries (Separação Canônica entre I/O e Iteração)
*   **Principle**: Isole operações de I/O (leitura de disco, requisições de rede, consultas a banco de dados) ou transformações de múltiplos parâmetros em uma variável intermediária expressiva (*Explaining Variable* de Martin Fowler) antes de iniciar laços de iteração (`data = read_manifest_lines(path); for item in data:`). Reserve iterações inline (`for x in obj.method():`) estritamente para views de estruturas em memória $O(1)$ (`dict.values()`, `dict.items()`) ou geradores lazy de streaming.
*   **Application in Cresmo**:
    *   `DiscoverBatchSourcesUseCase._classify_seeds`: define `main_urls = read_manifest_lines(playlist_path)` antes do `for mu in main_urls:`, isolando domínios de falha de disco (`FileNotFoundError`, permissões), permitindo inspeção em breakpoints antes da primeira iteração e conferindo semântica de Ubiquitous Language às linhas brutas de arquivo.

### 8.10 Defensive Programming & Boundary Guarding (Programação Defensiva Canônica)
*   **Principle**: O sistema deve proteger ativamente sua estabilidade operacional na fronteira externa (ingestão de arquivos, parsing de metadados, rede e adaptadores), blindando o núcleo de domínio contra dados incompletos, identificadores ambíguos ou corrupção de estado:
    1.  *Multi-Key / Alias Resolution*: Estruturas de índice em memória mantêm chaves canônicas e variantes legíveis (ex.: ID canônico de 11 caracteres e `Path.stem` amigável) para suportar variações legítimas de nomenclatura sem quebras de lookup.
    2.  *Guards no Nascimento (Fail-Fast)*: Value Objects e Pydantic Settings validam invariantes estritamente no momento de instanciação (`__post_init__`). Dentro do Domínio (*Trusted Core*), os objetos são assumidos íntegros por definição, eliminando verificações defensivas redundantes no coração das regras de negócio.
    3.  *Fallback Gracioso e Determinado*: Fornecimento de provedores ou comportamentos padrão previsíveis (ex.: fallbacks de prompt provider) quando injeções opcionais não são passadas, garantindo que o pipeline permaneça operacional e testável.
*   **Application in Cresmo**:
    *   `DiscoverBatchSourcesUseCase._scan_raw_lake`: popula defensivamente `local_video_to_channel` com ambos `canonical_vid` e `stem`, garantindo resolução imediata de canais mesmo quando arquivos brutos contêm títulos legíveis em vez de IDs puros de vídeo.

### 8.11 GRASP High Cohesion & Information Expert (Perito na Informação e Alta Coesão)
*   **Principle**: Atribuir a responsabilidade de executar uma operação ao elemento que detém a informação necessária para cumpri-la (*Information Expert*). Manter comportamentos que consomem atributos internos dentro da própria classe (*High Cohesion*), evitando expor estruturas internas para funções utilitárias externas dispersas.
*   **Application in Cresmo**:
    *   `DiscoverBatchSourcesUseCase._notify`: encapsula privadamente a validação defensiva e o disparo de mensagens de status via `self.progress_callback`, mantendo o caso de uso como autoridade coesa e autossuficiente sobre suas notificações de progresso, sem vazar a gestão de callbacks para funções externas.

---

## 9. Architectural Anti-Patterns Catalog & Prohibited Practices

To preserve architectural purity and prevent gradual erosion of the Hexagonal and Clean DDD boundaries across the Cresmo codebase, the following anti-patterns are explicitly prohibited:

### 9.1 Anti-Pattern: Lazy Happy-Path Micro-Optimization (Instanciação Redundante de Configuração)
*   **Definition**: Postponing or conditionally instantiating central configuration objects (`CresmoSettings`) under the premise of "optimizing" single-item runs, while an earlier call in the flow (e.g., `build_pipeline()`) already instantiates the same configuration.
*   **Violation**: Creates multiple copies of configuration in memory, duplicates `.env` parsing/validation I/O, obscures where settings originate, and prevents consistent parameter overrides.
*   **Prescribed Pattern (Fail-Fast Single Source of Truth)**: Instantiate `settings = CresmoSettings()` once at the entrypoint controller (`handle_run`), mutate/override operational parameters explicitly, and inject the identical instance down into `build_pipeline(settings=settings)` and all downstream use cases.

### 9.2 Anti-Pattern: Dependency Inversion Violation (A Aplicação Conhecer a Apresentação)
*   **Definition**: Allowing Application or Domain services (e.g., `pipeline.py`, use cases, entities) to import, reference, or call presentation abstractions (e.g., `argparse.Namespace`, `cli.py`, `sys.stdout`, exit codes).
*   **Violation**: Breaks the core Dependency Rule of Clean Architecture. Renders business logic untestable without mock terminal environments and prevents reusing the engine in APIs, queues, or webhooks.
*   **Prescribed Pattern**: Presentation layer imports and depends on Application/Domain. Application/Domain never imports Presentation. All CLI-specific behaviors (exit code translation, console formatting) reside strictly in `cresmo/presentation/`.

### 9.3 Anti-Pattern: Monolithic Aggregate / God Aggregate (O "Agregado Frankenstein")
*   **Definition**: Lumping distinct entities that have independent transactional lifecycles (e.g., combining all YouTube channels, transcripts, notes, and user preferences) into a single giant Aggregate Root.
*   **Violation**: Creates transactional bottlenecks, memory bloat, and massive locking contention. An Aggregate is strictly the boundary of immediate transactional consistency.
*   **Prescribed Pattern**: Keep Aggregate Roots small and cohesive. Independent entities communicate asynchronously or are orchestrated across boundaries via Application Use Cases.

### 9.4 Anti-Pattern: Primitive Obsession & Anemic Domain Model
*   **Definition**: Passing raw strings, dicts, or tuples across domain boundaries instead of strongly-typed, self-validating Value Objects (e.g., using `str` instead of `ContentId`, `VideoUrl`, or `ChannelSlug`).
*   **Violation**: Invariants cannot be guaranteed at birth; business validation logic leaks into controllers, presenting high risk of corrupt state.
*   **Prescribed Pattern**: Value Objects are immutable, self-validating on creation, and encapsulate structural invariants permanently.

### 9.5 Anti-Pattern: Hardcoded Relative Path Resolution (Fragilidade Estrutural de Diretórios)
*   **Definition**: Resolving workspace root via hardcoded parent climbing (e.g., `Path(__file__).parents[3]`).
*   **Violation**: Breaks immediately when files are refactored into submodules or executed from alternate working directories.
*   **Prescribed Pattern**: Resilient Anchor-Marker discovery (`pyproject.toml` / `.git` / `.cresmo-root`) documented in [ADR-006](ADR-006-resilient-workspace-root-discovery.md).

### 9.6 Anti-Pattern: Duplicate Pipeline Stage Orchestration (Violação de DRY em Workflows)
*   **Definition**: Repeating sequential transformation stages across different input modalities (e.g., duplicating Stages 2–7 for video vs. text files).
*   **Violation**: Leads to cognitive drift, maintenance overhead, and uneven bug fixes across entrypoints.
*   **Prescribed Pattern**: Template Method pattern extracting the invariant transformation skeleton into private orchestrators (`_synthesize_transcript`), documented in [ADR-007](ADR-007-pipeline-template-method-dry.md).

### 9.7 Anti-Pattern: Speculative Generality (Generalidade Especulativa / Complexidade Prematura)
*   **Definition**: Adding extra layers of abstraction, unused generic type wrappers, phantom interfaces, or configuration parameters anticipating hypothetical future requirements that do not currently exist.
*   **Violation**: Increases cognitive load, introduces noise and indirection, and complicates unit test mocking without delivering operational value (violating YAGNI — *You Aren't Gonna Need It* and KISS).
*   **Prescribed Pattern**: Implement the leanest concrete solution that satisfies current invariants. Refactor toward abstraction only when two or more distinct concrete use cases emerge.

### 9.8 Anti-Pattern: Lazy Class / Lazy Function & Middleman Indirection
*   **Definition**: Creating wrapper functions or classes that do nothing more than immediately pass parameters to another function (e.g., wrapping `handle_run` inside a redundant `execute()` just to host an `if/else`).
*   **Violation**: Adds friction to code navigation and debugger call stacks (*Middleman code smell*), diluting responsibility between functions.
*   **Prescribed Pattern**: The canonical entrypoint handler (`handle_run`) is the legitimate dispatcher; conditional branching and workflow selection belong directly inside it without intermediate forwarding layers.

### 9.9 Anti-Pattern: Linear Scan Queue Degradation ($O(N^2)$ Membership Lookups)
*   **Definition**: Validar duplicatas diretamente contra uma lista de despacho linear (`if item not in dispatch_queue: dispatch_queue.append(item)`) dentro de laços de iteração sobre coleções, arquivos de lago ou feeds remotos.
*   **Violation**: Degrada a complexidade algorítmica de linear $O(N)$ para quadrática $O(N^2)$, criando gargalos severos de CPU e latência à medida que o volume de fontes cresce.
*   **Prescribed Pattern**: Padrão *Ordered Unique Queue* (§8.8), associando um `set` de controle para consultas $O(1)$ à lista de agendamento ordenado.

### 9.10 Anti-Pattern: Obfuscated I/O Loop Header (Conflated Fetch-and-Loop)
*   **Definition**: Executar I/O de disco, consultas a bancos de dados ou chamadas externas de rede diretamente na expressão de iteração do laço (ex.: `for line in read_manifest_lines(path):`).
*   **Violation**: Aglutina a fase de aquisição/transporte de dados com a fase de processamento/algoritmo. Em caso de falha de disco ou rede, o stack trace obscurece a fronteira de erro, além de impedir a inspeção do estado completo em breakpoints antes do laço.
*   **Prescribed Pattern**: Padrão *Explaining Variable on I/O Boundaries* (§8.9), extraindo o carregamento em linha própria antes do laço.

### 9.11 Anti-Pattern: Noise Variable Indirection (Variáveis Intermediárias Supérfluas)
*   **Definition**: Atribuir propriedades nativas e views em memória já autoexplicativas a variáveis temporárias descartáveis (ex.: `channels = local_channels.values(); for c in channels:`) quando nenhuma semântica adicional é introduzida.
*   **Violation**: Introduz poluição visual e carga cognitiva desnecessária no escopo local sem qualquer benefício arquitetural.
*   **Prescribed Pattern**: Iterar diretamente sobre a view de memória (`for c in local_channels.values():`).

### 9.12 Anti-Pattern: Fragile Ingestion / Blind Trust Boundary (Ingestão Frágil sem Programação Defensiva)
*   **Definition**: Assumir ingenuamente que arquivos brutos, metadados externos ou fontes de terceiros sempre estarão em conformidade estrita com um único formato idealizado (ex.: supor que arquivos Markdown no lago sempre terão o nome do ID do vídeo, falhando com `KeyError` ou pulando fontes silenciosamente quando nomeados com títulos humanizados).
*   **Violation**: Provoca quebras súbitas em tempo de execução ou perda silenciosa de itens durante processamentos em lote no lago de dados.
*   **Prescribed Pattern**: Padrão *Defensive Programming & Boundary Guarding* (§8.10), estabelecendo resolução por múltiplos identificadores (aliases) e parsing defensivo de frontmatter.

### 9.13 Anti-Pattern: Exception Swallowing / Pseudo-Defensive Blind Catch (Mascaramento Silencioso de Falhas)
*   **Definition**: Utilizar blocos amplos `try/except Exception: pass` sob o pretexto de "código defensivo", silenciando falhas críticas sem auditoria, telemetria ou logging estruturado.
*   **Violation**: Viola o princípio *Fail-Fast*, mascara corrupção de dados e invalida o diagnóstico por SRE e observabilidade (Prometheus/Grafana/Loki).
*   **Prescribed Pattern**: Captura cirúrgica de exceções esperadas com tratamento de contingência documentado ou propagação explícita mapeada para a taxonomia de códigos de saída da CLI (§2.4).

### 9.14 Anti-Pattern: Helper/Utils Dumpster (A "Lixeira" de Utilitários Genéricos)
*   **Definition**: Criar módulos ou arquivos amorfos nomeados como `helpers.py`, `utils.py`, `common.py` ou `misc.py` para abrigar funções dispersas sem Bounded Context, sem Ubiquitous Language e sem dono conceitual claro.
*   **Violation**: Incentiva a programação puramente procedural e desconexa, atrai acoplamento desordenado (*spaghetti code*), oculta violações do Princípio da Responsabilidade Única (SRP) e atua como o principal catalisador de dependências circulares e código zumbi.
*   **Prescribed Pattern**: Manter a lógica coesa dentro da classe detentora da informação (*Information Expert*, §8.11) ou, caso represente um comportamento reutilizável entre múltiplos serviços, formalizá-lo como um Domain Service ou Application Service semântico, com nome explícito em inglês e pertencente a um Bounded Context bem definido.

### 9.15 Anti-Pattern: Broken Encapsulation & Feature Envy (Quebra de Encapsulamento e Inveja de Recursos)
*   **Definition**: Extrair lógica que consome exclusivamente atributos de um objeto para uma função ou helper externo (ex.: criar uma função utilitária `notify_progress(callback, message)` forçando quem a chama a passar `self.progress_callback` a cada invocação).
*   **Violation**: Viola a Lei de Deméter e o princípio "Tell, Don't Ask". Expõe detalhes internos da classe para o ecossistema externo, dilui os limites de encapsulamento e cria dependências frágeis entre a estrutura de dados da classe e funções acessórias.
*   **Prescribed Pattern**: Princípio *Information Expert* (GRASP, §8.11): se o método necessita de dados internos da instância, ele deve ser um método (público ou privado) pertencente à própria classe.

### 9.16 Anti-Pattern: Low Cohesion & Gratuitous Decomposition (Fragmentação Arbitrária e Baixa Coesão - Violação GRASP/Clean Code)
*   **Definition**: Fragmentar classes ou métodos coesos em múltiplos arquivos minúsculos de poucas linhas sob o pretexto de "manter tudo pequeno", espalhando fluxo de controle conexo por módulos periféricos artificiais.
*   **Violation**: Degrada a Developer Experience (DX) e a navegabilidade do código (*shotgun surgery*), aumenta exponencialmente a carga cognitiva para rastrear um fluxo de execução simples e dilui a fronteira do caso de uso.
*   **Prescribed Pattern**: Princípio de Alta Coesão (*High Cohesion* do GRASP, §8.11) e Clean Code: manter partes fortemente relacionadas juntas no mesmo módulo, extraindo componentes apenas quando houver justificativa clara de reuso por múltiplos atores ou fronteira explícita de arquitetura hexagonal (Portas e Adaptadores).

---

## 10. References

- Predecessor ADR: [`docs/adr/ADR-001-cresmo-modular-monolith-strangling.md`](ADR-001-cresmo-modular-monolith-strangling.md)
- Context & Ubiquitous Language: [`CONTEXT.md`](../../CONTEXT.md)
- Ubiquitous Language Glossary: [`docs/GLOSSARY.md`](../GLOSSARY.md)
- Method Specification: [`.agents/skills/stangler-doctor/SKILL.md`](../../.agents/skills/stangler-doctor/SKILL.md)


