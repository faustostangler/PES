# Cresmo Playground Storage (ARCHIVED)

> [!WARNING]
> The active, production-grade persistent data stores have been moved out of `playground/cresmo/` into dedicated, semantic top-level directories:
> - **Data Lake (`data/`)**: Contains Bronze tier raw media transcripts (`data/raw/`), Silver tier enriched multi-pass compendiums (`data/enriched/`), and the SQLite WAL idempotency ledger (`data/cresmo_ledger.db`).
> - **Obsidian Second Brain Vault (`vault/`)**: Contains Gold tier atomic notes (`vault/concepts/`, `vault/entities/`, `vault/events/`, `vault/processes/`), Maps of Content (`vault/MOCs/`), and the master index (`vault/_index.json`).
>
> Do not write new data into `playground/cresmo/`. All CLI tools, pipeline use cases, and Docker containers mount and operate on `/app/data` and `/app/vault`.
