# Context Map — PES Knowledge Ecosystem

## Bounded Contexts

1. **[Cresmo Knowledge Synthesis](./CONTEXT.md) (Core Subdomain)**
   - **Responsibility**: Multi-pass Socratic gap analysis, Braudelian longitudinal expansion, Jaspers synchronic cross-sections, two-phase atomic note synthesis, and Map of Content (MOC) reconciliation.
   - **Purity**: Clean Hexagonal Architecture, pure Python domain, zero framework dependencies, strict Value Objects and Aggregates.

2. **[Legacy Media Ingestion](./docs/legacy_discovery/DISCO-001-cresmo-ecosystem-archaeology.md) (Supporting Subdomain)**
   - **Responsibility**: Channel/playlist crawling, YouTube subtitle extraction, HTTP 429 rate-limiting mitigation, Netscape cookie rotation, and Whisper fallback audio transcription.
   - **Classification**: Non-conformant legacy codebase (`playground/isb.ai/`). Protected behind an Anti-Corruption Layer (ACL).

3. **[Obsidian Second Brain Vault](./docs/architecture/vault_persistence_specification.md) (Generic Subdomain)**
   - **Responsibility**: Local markdown storage, YAML frontmatter schemas, folder typologies (`wiki/<note_type>/`), tiered index lookups (`_index.json`), and bidirectional graph visualization.
   - **Classification**: Target persistence boundary accessed exclusively through `VaultRepositoryPort`.

---

## Strategic Relationships & Boundaries

```mermaid
graph LR
    subgraph Upstream ["Upstream: Supporting Subdomain"]
        LegacyIngestion["Legacy Media Ingestion<br>(playground/isb.ai)"]
    end

    subgraph Core ["Core Domain: Cresmo Knowledge Synthesis"]
        ACL["Anti-Corruption Layer (ACL)<br>(MediaIngestionPort Adapter)"]
        DomainCore["Domain & Application Core<br>(src/cresmo/)"]
    end

    subgraph Downstream ["Downstream: Generic Subdomain"]
        VaultRepo["Obsidian Second Brain<br>(VaultRepositoryPort Adapter)"]
    end

    LegacyIngestion -->|Raw Transcripts & DTOs| ACL
    ACL -->|Domain Entities (RawTranscript)| DomainCore
    DomainCore -->|Atomic Notes & MOCs| VaultRepo
```

### Upstream Relationship: Legacy Media Ingestion → Cresmo Core
- **Pattern**: Customer-Supplier with **Anti-Corruption Layer (ACL)**.
- **Contract**: `MediaIngestionPort` in `src/cresmo/application/ports.py`.
- **Rule**: `src/cresmo/domain/` and `src/cresmo/application/` MUST NEVER import or reference `playground/isb.ai/`, `yt-dlp`, or `openai-whisper`. All translation and `sys.path` isolation happen strictly within `LegacyISBMediaIngestionAdapter`.

### Downstream Relationship: Cresmo Core → Obsidian Second Brain
- **Pattern**: Repository Port abstraction.
- **Contract**: `VaultRepositoryPort` in `src/cresmo/application/ports.py`.
- **Rule**: Business logic in use cases never performs direct filesystem I/O (`Path.write_text()`, `Path.read_text()`). All vault storage, frontmatter serialization, index updating, and `.tmp` atomic writing are encapsulated inside `ObsidianVaultAdapter`.
