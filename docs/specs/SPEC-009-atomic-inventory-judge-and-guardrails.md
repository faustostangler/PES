# SPEC-009: Atomic Inventory Discovery Judge and Guardrails Specification

**Context:** Cresmo Knowledge Synthesis  
**Phase:** Phase 2 — Refractometry (Precision Test Specifications)  
**Status:** APPROVED SPECIFICATION  
**Governing ADR:** [`ADR-024`](../adr/ADR-024-iterative-llm-as-a-judge-atomic-inventory-discovery.md)  
**Related Specs:** [`SPEC-001`](SPEC-001-cresmo-core.md), [`EVAL-001`](EVAL-001-cresmo-synthesis.md)  

---

## 1. Domain Invariants and Gate 1 Contract

The deterministic guardrail function `is_valid_inventory_json_structure(data: Any) -> bool` must evaluate:
1. `isinstance(data, list)` and `len(data) > 0`.
2. Every item `entry` in `data` satisfies:
   - `isinstance(entry, dict)`
   - `isinstance(entry.get("title"), str)` and `bool(entry["title"].strip())`
   - `isinstance(entry.get("type"), str)` and `entry["type"].lower() in {"entity", "concept", "event", "process"}`
   - If `entry["type"].lower() == "event"`, `bool(re.match(r"^\d{4}", entry["title"].strip()))` must be `True`.

If any condition fails, Gate 1 returns `False`.

---

## 2. Gate 2 LLM-as-a-Judge Contract

1. Prompt Provider Contract:
   ```python
   def get_judge_inventory_prompt(
       self,
       compendium_title: str,
       channel_name: str,
       compendium_body: str,
       inventory_json: str,
   ) -> tuple[str, str]:
       """Generate system instruction and user prompt for inventory judge."""
   ```
2. Judge execution parameters:
   - `temperature = 0.0`
   - Deterministic boolean parser `parse_judge_boolean(raw_output: str) -> bool` (verdict true if response starts with or strictly contains "true" case-insensitively).

---

## 3. Retry and Telemetry Invariants

1. `max_rewrites` parameter:
   - If `max_rewrites <= 0`: unbounded retries.
   - If `max_rewrites > 0`: bounded to `max_rewrites` retry attempts.
2. Telemetry Trace IDs:
   - Extraction: `{content_id}_inventory` (initial) / `{content_id}_inventory_retry_{attempt}`
   - Judge: `{content_id}_inventory_judge` (initial) / `{content_id}_inventory_judge_retry_{attempt}`
3. Failure handling:
   - If retry budget exhausted and judge verdict remains `False`, the use case raises `DomainValidationError`.
