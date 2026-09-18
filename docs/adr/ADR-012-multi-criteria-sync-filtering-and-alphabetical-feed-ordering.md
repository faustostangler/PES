# ADR-012: Multi-Criteria Synchronization Filtering and Alphabetical Feed Ordering

**Status:** APPROVED  
**Date:** 2026-09-17  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith)  
**Related ADRs:** [ADR-001](ADR-001-cresmo-modular-monolith-strangling.md), [ADR-002](ADR-002-cresmo-presentation-cli.md), [ADR-003](ADR-003-pes-production-architecture.md), [ADR-009](ADR-009-streaming-batch-source-discovery-producer-consumer.md), [ADR-010](ADR-010-zero-legacy-shims-and-streaming-first-unification.md)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Context & Architectural Drivers

During media ingestion and batch synthesis in the Cresmo Knowledge Monolith, operators frequently need to scope execution to specific subsets of content rather than ingesting entire channel catalogs. The legacy playground (`playground/cresmo` and `playground/isb.ai`) provided rudimentary filtering capabilities (e.g. `--category` filtering in `cresmo_pipeline.py`, `--channel` directory targeting in `index_raw_transcripts.py`, and alphabetical channel syncing in `master_git_sync.py`).

However, the initial hexagonal implementation in `src/cresmo` introduced structural limitations:
1. **Rigid Single-Channel Sync:** `cresmo sync` (`src/cresmo/presentation/commands/sync.py`) mandated a single required `--channel <url>`, preventing bulk synchronization of playlists or manifests with selective filters.
2. **Missing Multi-Criteria Scoping:** Neither `cresmo sync` nor `cresmo run` provided CLI flags to filter workloads by channel names/handles, taxonomy categories, or discrete video IDs.
3. **Non-Deterministic Probing Order:** In `DiscoverBatchSourcesUseCase`, channel seeds were collected and probed in arbitrary dictionary/hash-set order, causing non-reproducible run logs and inconsistent checkpoint progression.
4. **Lack of Comma-Separated Multi-Value Inputs:** Operators could not pass multiple targets (e.g. `--category politics_br,tech_ai` or `--channel "Ancapsu,3Blue1Brown"`).
5. **Category Duality:** The domain taxonomy in `src/cresmo/domain/taxonomy.py` classifies channels into both a domain name (`politics_br`, `tech_ai`, `history`, `philosophy`, `finance`, etc.) and a volatility category (`perennial`, `volatile`). Filtering must evaluate both dimensions seamlessly.

---

## 2. Decision

We establish five binding architectural standards for feed synchronization and batch discovery:

### 2.1 Domain Value Object: `SyncFilterCriteria`
We introduce an immutable, frozen Domain Value Object `SyncFilterCriteria` in `src/cresmo/domain/value_objects.py`:
```python
@dataclass(frozen=True)
class SyncFilterCriteria:
    channels: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    video_ids: tuple[str, ...] = ()
```
**Invariants & Domain Methods:**
- **Sanitization:** All tokens are stripped of whitespace, lowercased where appropriate, and empty elements are rejected during construction.
- **`matches_channel(channel_name: str, channel_url: str | None = None) -> bool`**: Returns `True` if `channels` is empty (default full flow) or if `channel_name` (or handle/URL substring) matches any configured channel filter case-insensitively.
- **`matches_category(channel_name: str) -> bool`**: Uses the pure domain taxonomy `classify_channel(channel_name) -> tuple[domain, category_type]`. Returns `True` if `categories` is empty, OR if `domain.lower() in categories` OR `category_type.lower() in categories`. This enables filtering simultaneously by domain name (e.g., `politics_br`) and volatility category (e.g., `perennial`).
- **`matches_video(video_id: str, video_url: str | None = None) -> bool`**: Returns `True` if `video_ids` is empty, or if the video ID or URL matches any item in `video_ids`.
- **`is_empty() -> bool`**: Returns `True` when no filter criteria are active.

### 2.2 Default Full Pipeline Flow Principle
- If **no** filter flag (`--channel`, `--category`, `--video`) is specified, the system executes in **full pipeline flow** across all configured channels in the manifest (`data/playlist.txt`), applying zero exclusionary filters.
- Filtering is **strictly opt-in** and activates only for explicitly specified criteria.

### 2.3 Strict Deterministic Alphabetical Channel Ordering
- When discovering, probing feeds, or synchronizing channels across manifests or lakes, candidate channels **MUST ALWAYS** be sorted in strict case-insensitive alphabetical order (`key=lambda c: c.lower()`) before any network probe or download is dispatched.
- This applies universally to:
  1. `DiscoverBatchSourcesUseCase`: Sorting `channels_to_probe` prior to Stage A notifications and Stage B feed probing.
  2. `SyncChannelUseCase` / `cresmo sync`: Multi-channel manifest synchronization proceeds channel-by-channel in alphabetical order.

### 2.4 Multi-Value Comma-Separated CLI Parameter Support
All filter arguments across both `cresmo sync` and `cresmo run` must support both multi-argument format (`--channel A B`) and comma-separated tokens (`--channel A,B`), parsed into clean tuples:
- `--channel`, `--channels`: Comma/space-separated channel names, handles, or URLs.
- `--category`, `--categories`, `-c`: Comma/space-separated domain names or volatility types.
- `--video`, `--video-id`: Comma/space-separated video identifiers or URLs.

### 2.5 Presentation Layer Integration (`cresmo sync` & `cresmo run`)
- In `cresmo sync` (`src/cresmo/presentation/commands/sync.py`), `--channel` is no longer mandatory. When omitted, `cresmo sync` reads from the manifest playlist (`--manifest` or `data/playlist.txt`) and applies any active filters in alphabetical order.
- In `cresmo run` (`src/cresmo/presentation/commands/run.py`), `--channel`, `--category`, and `--video` flags are propagated directly into `BatchDiscoveryQuery.filter_criteria`.

---

## 3. Consequences & Trade-Offs

### Positive
1. **Operator Usability & DX:** Allows granular, targeted synchronization without requiring manual modification of seed playlist files.
2. **Deterministic Reproducibility:** Alphabetical channel processing ensures identical ordering across different runtime environments and platforms.
3. **Domain Integrity:** Filtering logic is encapsulated in pure domain Value Objects, keeping CLI presentation thin (Humble Object pattern) and infrastructure adapters free from business filtering rules.
4. **Category Duality Handling:** Seamlessly supports filtering by specific domains (`tech_ai`) or macro volatility classes (`perennial`, `volatile`) in a single unified parameter list.

### Negative / Neutral
1. **Channel Sorting Overhead:** Sorting channel strings in memory is $O(N \log N)$, requiring $< 1$ms for standard playlists ($\le 500$ channels), representing negligible latency.

---

## 4. Compliance Verification

- [x] Hexagonal Architecture layers respected (Domain $\rightarrow$ Application $\rightarrow$ Presentation).
- [x] Zero framework dependencies in Domain Value Objects (`SyncFilterCriteria`).
- [x] Invariants enforced at construction (`__post_init__`).
- [x] Mirrored unit tests in `tests/cresmo/unit/test_channel_sync_vo.py`, `tests/cresmo/unit/test_discover_batch_sources.py`, and `tests/cresmo/unit/test_cli.py`.
