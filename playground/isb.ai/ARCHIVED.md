# Archived Legacy Subsystem: ISB.AI Playground

**Status**: `DECOMMISSIONED / READ-ONLY ARCHIVE`  
**Governing ADR**: [`docs/adr/ADR-004-native-media-ingestion-decommissioning.md`](../../docs/adr/ADR-004-native-media-ingestion-decommissioning.md)  
**Superseded by**: [`src/cresmo/infrastructure/adapters/native_media_ingestion_adapter.py`](../../src/cresmo/infrastructure/adapters/native_media_ingestion_adapter.py)

---

## Notice of Archival

As of the completion of **Etapa II (Trilha 4)** of the PES Modular Monolith roadmap, this directory (`playground/isb.ai/`) is officially archived and decommissioned.

1. **No Runtime Dependencies**: The core production code in `src/cresmo` does not import or depend on any modules in this directory.
2. **Native Replacement**: All media ingestion, YouTube subtitle extraction (JSON3 timedtext), whisper speech-to-text fallback, and channel feed discovery have been migrated natively to `NativeMediaIngestionAdapter`.
3. **Preservation**: This code is preserved solely for historical reference and comparative algorithmic benchmarks. Do not add new features or production integrations to this directory.
