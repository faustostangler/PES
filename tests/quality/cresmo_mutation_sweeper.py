"""SOTA Mutation Sweeper for Cresmo (Phase 4: Treatment).

Executes targeted, wave-based mutation testing across all layers of Cresmo
following the Doctor Stangler Architecture Method:
- Domain Core: 0 Survivors (100% Kill Rate)
- Application: 0 Survivors (100% Kill Rate)
- Infrastructure: < 5% Survivors (>95% Kill Rate)
- Presentation: Regression coverage

Features:
- Automated source tree synchronization to prevent stale cache drift
- Dynamic test-to-module mapping to eliminate mutmut 'No Tests' false positives
- Isolated per-module or wave-based execution
- Fail-safe pyproject.toml configuration management
- Detailed survivor diff inspection

Usage:
    uv run python tests/quality/cresmo_mutation_sweeper.py --wave domain
    uv run python tests/quality/cresmo_mutation_sweeper.py --file src/cresmo/domain/entities/identity.py
    uv run python tests/quality/cresmo_mutation_sweeper.py --file src/cresmo/domain/entities/identity.py --show-survivors
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

# Mapping of source modules/patterns to their mirrored unit test suites
MODULE_TEST_MAP: dict[str, list[str]] = {
    # Wave 1: Domain Entities
    "src/cresmo/domain/entities/identity.py": [
        "tests/cresmo/unit/test_entities.py",
    ],
    "src/cresmo/domain/entities/transcripts.py": [
        "tests/cresmo/unit/test_entities.py",
    ],
    "src/cresmo/domain/entities/notes.py": [
        "tests/cresmo/unit/test_entities.py",
    ],
    "src/cresmo/domain/entities/compendium.py": [
        "tests/cresmo/unit/test_entities.py",
    ],
    # Wave 1: Domain Value Objects
    "src/cresmo/domain/value_objects/identity.py": [
        "tests/cresmo/unit/test_value_objects.py",
        "tests/cresmo/unit/test_batch_id.py",
        "tests/cresmo/unit/test_channel_sync_vo.py",
    ],
    "src/cresmo/domain/value_objects/sync.py": [
        "tests/cresmo/unit/test_channel_sync_vo.py",
        "tests/cresmo/unit/test_value_objects.py",
    ],
    "src/cresmo/domain/value_objects/prompt.py": [
        "tests/cresmo/unit/test_chat_prompt_vo.py",
        "tests/cresmo/unit/test_value_objects.py",
    ],
    "src/cresmo/domain/value_objects/media.py": [
        "tests/cresmo/unit/test_channel_sync_vo.py",
        "tests/cresmo/unit/test_value_objects.py",
    ],
    "src/cresmo/domain/value_objects/ledger.py": [
        "tests/cresmo/unit/test_channel_sync_vo.py",
        "tests/cresmo/unit/test_raw_index_entry_vo.py",
        "tests/cresmo/unit/test_value_objects.py",
    ],
    "src/cresmo/domain/value_objects/notes.py": [
        "tests/cresmo/unit/test_value_objects.py",
    ],
    "src/cresmo/domain/value_objects/quality.py": [
        "tests/cresmo/unit/test_quality_vo.py",
        "tests/cresmo/unit/test_value_objects.py",
    ],
    "src/cresmo/domain/value_objects/constants.py": [
        "tests/cresmo/unit/test_domain_constants.py",
        "tests/cresmo/unit/test_value_objects.py",
    ],
    "src/cresmo/domain/stage_registry.py": [
        "tests/cresmo/unit/test_stage_registry.py",
    ],
    "src/cresmo/domain/taxonomy.py": [
        "tests/cresmo/unit/test_taxonomy.py",
    ],
    # Wave 2: Application Pipeline Engine
    "src/cresmo/application/pipeline/quarantine.py": [
        "tests/cresmo/unit/test_stage_runner_quarantine.py",
    ],
    "src/cresmo/application/pipeline/stage_runner.py": [
        "tests/cresmo/unit/test_stage_runner.py",
        "tests/cresmo/unit/test_stage_runner_quarantine.py",
    ],
    "src/cresmo/application/pipeline/stage_descriptor.py": [
        "tests/cresmo/unit/test_stage_descriptor_runner.py",
    ],
    "src/cresmo/application/pipeline/stage_factory.py": [
        "tests/cresmo/unit/test_stage_factory.py",
    ],
    "src/cresmo/application/pipeline/transcript_loader.py": [
        "tests/cresmo/unit/test_transcript_loader.py",
    ],
    "src/cresmo/application/pipeline/coordinator.py": [
        "tests/cresmo/unit/test_pipeline.py",
        "tests/cresmo/unit/test_pipeline_telemetry.py",
        "tests/cresmo/unit/test_pipeline_coordinator.py",
    ],
    "src/cresmo/application/pipeline/context.py": [
        "tests/cresmo/unit/test_pipeline_execution_context.py",
        "tests/cresmo/unit/test_stage_foundation.py",
        "tests/cresmo/unit/test_stage_runner.py",
    ],
    "src/cresmo/application/pipeline/models.py": [
        "tests/cresmo/unit/test_pipeline_models.py",
        "tests/cresmo/unit/test_stage_foundation.py",
    ],
    # Wave 3: Application Use Cases
    "src/cresmo/application/use_cases/concat_master.py": [
        "tests/cresmo/unit/test_concat_master_use_case.py",
    ],
    "src/cresmo/application/use_cases/fill_gaps.py": [
        "tests/cresmo/unit/test_use_cases.py",
    ],
    "src/cresmo/application/use_cases/expand_compendium.py": [
        "tests/cresmo/unit/test_use_cases.py",
    ],
    "src/cresmo/application/use_cases/transform_fluid_prose.py": [
        "tests/cresmo/unit/test_use_cases.py",
    ],
    "src/cresmo/application/use_cases/unify_duplicate_notes.py": [
        "tests/cresmo/unit/test_unify_duplicates.py",
    ],
    "src/cresmo/application/use_cases/discover_atomic_inventory.py": [
        "tests/cresmo/unit/test_discover_atomic_inventory_use_case.py",
    ],
    "src/cresmo/application/use_cases/discovery/discover_batch_sources.py": [
        "tests/cresmo/unit/test_discover_batch_sources.py",
    ],
    "src/cresmo/application/use_cases/indexing/index_raw_transcripts.py": [
        "tests/cresmo/unit/test_index_raw_transcripts_use_case.py",
    ],
    "src/cresmo/application/use_cases/ingest_raw_transcript.py": [
        "tests/cresmo/unit/test_ingest_raw_transcript_use_case.py",
    ],
    "src/cresmo/application/use_cases/reconcile_mocs.py": [
        "tests/cresmo/unit/test_reconcile_mocs_use_case.py",
    ],
    "src/cresmo/application/use_cases/sync_channel.py": [
        "tests/cresmo/unit/test_sync_channel_use_case.py",
    ],
    "src/cresmo/application/use_cases/synthesize_atomic_batch.py": [
        "tests/cresmo/unit/test_use_cases.py",
    ],
    # Wave 4: Infrastructure
    "src/cresmo/infrastructure/adapters/obsidian/adapter.py": [
        "tests/cresmo/unit/test_vault_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/obsidian/notes.py": [
        "tests/cresmo/unit/test_vault_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/obsidian/transcripts.py": [
        "tests/cresmo/unit/test_vault_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/obsidian/mocs.py": [
        "tests/cresmo/unit/test_vault_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/opentelemetry_adapter.py": [
        "tests/cresmo/unit/test_opentelemetry_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/prometheus_metrics_adapter.py": [
        "tests/cresmo/unit/test_prometheus_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/anonymizer_adapter.py": [
        "tests/cresmo/unit/test_anonymizer_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/cookie_extractor.py": [
        "tests/cresmo/unit/test_cookie_extractor.py",
    ],
}

WAVE_DEFINITIONS: dict[str, list[str]] = {
    "domain": [
        "src/cresmo/domain/entities/identity.py",
        "src/cresmo/domain/entities/transcripts.py",
        "src/cresmo/domain/entities/notes.py",
        "src/cresmo/domain/entities/compendium.py",
        "src/cresmo/domain/value_objects/identity.py",
        "src/cresmo/domain/value_objects/sync.py",
        "src/cresmo/domain/value_objects/prompt.py",
        "src/cresmo/domain/value_objects/media.py",
        "src/cresmo/domain/value_objects/ledger.py",
        "src/cresmo/domain/value_objects/notes.py",
        "src/cresmo/domain/value_objects/quality.py",
        "src/cresmo/domain/value_objects/constants.py",
        "src/cresmo/domain/stage_registry.py",
    ],
    "pipeline": [
        "src/cresmo/application/pipeline/quarantine.py",
        "src/cresmo/application/pipeline/stage_runner.py",
        "src/cresmo/application/pipeline/stage_descriptor.py",
        "src/cresmo/application/pipeline/stage_factory.py",
        "src/cresmo/application/pipeline/transcript_loader.py",
        "src/cresmo/application/pipeline/coordinator.py",
        "src/cresmo/application/pipeline/context.py",
        "src/cresmo/application/pipeline/models.py",
    ],
    "use_cases": [
        "src/cresmo/application/use_cases/concat_master.py",
        "src/cresmo/application/use_cases/fill_gaps.py",
        "src/cresmo/application/use_cases/expand_compendium.py",
        "src/cresmo/application/use_cases/transform_fluid_prose.py",
        "src/cresmo/application/use_cases/unify_duplicate_notes.py",
        "src/cresmo/application/use_cases/discover_atomic_inventory.py",
        "src/cresmo/application/use_cases/discovery/discover_batch_sources.py",
        "src/cresmo/application/use_cases/indexing/index_raw_transcripts.py",
        "src/cresmo/application/use_cases/ingest_raw_transcript.py",
        "src/cresmo/application/use_cases/reconcile_mocs.py",
        "src/cresmo/application/use_cases/sync_channel.py",
        "src/cresmo/application/use_cases/synthesize_atomic_batch.py",
    ],
    "infra": [
        "src/cresmo/infrastructure/adapters/obsidian/adapter.py",
        "src/cresmo/infrastructure/adapters/obsidian/notes.py",
        "src/cresmo/infrastructure/adapters/obsidian/transcripts.py",
        "src/cresmo/infrastructure/adapters/obsidian/mocs.py",
        "src/cresmo/infrastructure/adapters/opentelemetry_adapter.py",
        "src/cresmo/infrastructure/adapters/prometheus_metrics_adapter.py",
        "src/cresmo/infrastructure/adapters/anonymizer_adapter.py",
        "src/cresmo/infrastructure/adapters/cookie_extractor.py",
    ],
}


def ensure_mutmut_dataclass_support() -> None:
    """Ensure mutmut libcst visitor supports @dataclass decorated classes."""
    try:
        import mutmut.mutation.file_mutation as fm
        fm_path = Path(fm.__file__)
        code = fm_path.read_text(encoding="utf-8")
        target_check = 'if isinstance(node, cst.ClassDef) and len(node.decorators):'
        if target_check in code and 'is_dc = all(' not in code:
            old_block = '        if isinstance(node, cst.ClassDef) and len(node.decorators):\n            return True'
            new_block = (
                '        if isinstance(node, cst.ClassDef) and len(node.decorators):\n'
                '            is_dc = all(\n'
                '                (isinstance(d.decorator, cst.Name) and d.decorator.value == "dataclass")\n'
                '                or (\n'
                '                    isinstance(d.decorator, cst.Call)\n'
                '                    and isinstance(d.decorator.func, cst.Name)\n'
                '                    and d.decorator.func.value == "dataclass"\n'
                '                )\n'
                '                for d in node.decorators\n'
                '            )\n'
                '            if is_dc:\n'
                '                return False\n'
                '            return True'
            )
            if old_block in code:
                fm_path.write_text(code.replace(old_block, new_block), encoding="utf-8")
    except Exception:
        pass


def sync_source_to_mutants() -> int:
    """Synchronize src/ files to mutants/src/ and prune orphaned files."""
    ensure_mutmut_dataclass_support()
    src_dir = Path("src")
    mutants_dir = Path("mutants/src")
    count = 0
    for src_file in src_dir.glob("**/*"):
        if src_file.is_file() and not src_file.name.endswith((".pyc", ".pyo")):
            rel = src_file.relative_to(src_dir)
            target = mutants_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or src_file.read_bytes() != target.read_bytes():
                shutil.copy2(src_file, target)
                count += 1

    # Prune orphaned code files in mutants/src to prevent import shadowing
    if mutants_dir.exists():
        for p in list(mutants_dir.glob("**/*")):
            if p.is_file() and not p.name.endswith((".meta", ".spans", ".pyc", ".pyo")):
                rel = p.relative_to(mutants_dir)
                if not (src_dir / rel).exists():
                    p.unlink(missing_ok=True)

    # Also sync tests/
    tests_dir = Path("tests")
    mutants_tests_dir = Path("mutants/tests")
    for t_file in tests_dir.glob("**/*"):
        if t_file.is_file() and not t_file.name.endswith((".pyc", ".pyo")):
            rel = t_file.relative_to(tests_dir)
            target = mutants_tests_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or t_file.read_bytes() != target.read_bytes():
                shutil.copy2(t_file, target)
                count += 1
    return count



def collect_pytest_nodes(test_files: Sequence[str]) -> list[str]:
    """Collect pytest test node IDs for given test files."""
    cmd = ["uv", "run", "pytest", *test_files, "--collect-only", "-q"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    nodes: list[str] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if "::" in line and not line.startswith("="):
            nodes.append(line)
    return nodes


def extract_function_keys(source_path: Path) -> list[str]:
    """Parse python source file and return exact mutmut mangled function keys."""
    keys: list[str] = []
    # 1. Extract directly via AST using mutmut's canonical format_utils
    try:
        from mutmut.utils.format_utils import get_mutant_name, make_mutant_key
        content = source_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                mangled = make_mutant_key(node.name)
                keys.append(get_mutant_name(source_path, mangled))
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                        mangled = make_mutant_key(item.name, class_name=node.name)
                        keys.append(get_mutant_name(source_path, mangled))
    except Exception:
        pass

    # 2. Also check if metadata already has any additional keys
    try:
        from mutmut.__main__ import SourceFileMutationData
        from mutmut.utils.format_utils import get_mutant_name
        data = SourceFileMutationData(path=source_path)
        data.load()
        if data.hash_by_function_name:
            for f in data.hash_by_function_name:
                keys.append(get_mutant_name(source_path, f))
    except Exception:
        pass

    return sorted(set(keys))


def seed_mutmut_stats(source_path: Path, test_nodes: Sequence[str]) -> None:
    """Seed mutants/mutmut-stats.json with test mappings for all functions in the module."""
    stats_file = Path("mutants/mutmut-stats.json")
    data: dict[str, Any] = {}
    if stats_file.exists():
        try:
            data = json.loads(stats_file.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    tests_map = data.setdefault("tests_by_mangled_function_name", {})
    durations = data.setdefault("duration_by_test", {})
    func_hashes = data.setdefault("function_hashes", {})
    data.setdefault("stats_time", 1700000000.0)
    data.setdefault("function_dependencies", {})
    data.setdefault("config_fingerprint", {})
    data.setdefault("watched_file_hashes", {})
    data.setdefault("git_commit", None)

    for t in test_nodes:
        durations.setdefault(t, 0.05)

    fn_keys = extract_function_keys(source_path)
    for k in fn_keys:
        existing = set(tests_map.get(k, []))
        existing.update(test_nodes)
        tests_map[k] = sorted(existing)
        func_hashes[k] = "dummy_hash_for_mapping"

    stats_file.parent.mkdir(parents=True, exist_ok=True)
    stats_file.write_text(json.dumps(data, indent=4), encoding="utf-8")


def set_pyproject_only_mutate(target_path: str) -> str:
    """Set only_mutate in pyproject.toml and return original file content."""
    pyproject = Path("pyproject.toml")
    original = pyproject.read_text(encoding="utf-8")

    mutmut_section = "[tool.mutmut]\nsource_paths = [\"src\"]\n"
    if mutmut_section in original:
        new_content = original.replace(
            mutmut_section,
            f"{mutmut_section}only_mutate = [\"{target_path}\"]\n",
        )
        pyproject.write_text(new_content, encoding="utf-8")
    return original


def restore_pyproject(original_content: str) -> None:
    """Restore pyproject.toml to its original state."""
    Path("pyproject.toml").write_text(original_content, encoding="utf-8")


def run_mutation_on_module(
    source_path_str: str,
    reset: bool = True,
    show_survivors: bool = False,
) -> dict[str, int]:
    """Execute mutmut run on a single module with clean sync and mapped tests."""
    source_path = Path(source_path_str)
    if not source_path.exists():
        print(f"❌ Error: File not found: {source_path_str}")
        return {"total": 0, "killed": 0, "survived": 0}

    print(f"\n================================================================================")
    print(f"🎯 MUTATING MODULE: {source_path_str}")
    print(f"================================================================================")

    # 1. Sync
    synced = sync_source_to_mutants()
    if synced > 0:
        print(f"  ⚡ Synchronized {synced} source/test files to mutants/ tree.")

    # 2. Identify tests
    test_files = MODULE_TEST_MAP.get(source_path_str)
    if not test_files:
        # Fallback to test matching basename
        candidate = Path(f"tests/cresmo/unit/test_{source_path.name}")
        if candidate.exists():
            test_files = [str(candidate)]
        else:
            test_files = ["tests/cresmo/unit/test_entities.py", "tests/cresmo/unit/test_value_objects.py"]

    print(f"  🧪 Mirrored Test Suites: {', '.join(test_files)}")
    nodes = collect_pytest_nodes(test_files)
    print(f"  🔍 Collected {len(nodes)} test nodes for mapping.")

    # 3. Seed stats
    seed_mutmut_stats(source_path, nodes)

    # 4. Handle reset
    meta_path = Path("mutants") / f"{source_path_str}.meta"
    mutant_code_path = Path("mutants") / source_path
    if reset:
        mutant_code_path.unlink(missing_ok=True)
        if meta_path.exists():
            meta_path.unlink(missing_ok=True)
        print(f"  🔄 Cleared previous mutant artifacts for fresh generation.")

    # 5. Configure pyproject.toml & run
    original_pyproject = set_pyproject_only_mutate(source_path_str)
    try:
        print(f"  🚀 Executing 'uv run mutmut run'...")
        res = subprocess.run(
            ["uv", "run", "mutmut", "run"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode != 0:
            print(f"  ⚠️ mutmut warning / returncode {res.returncode}:")
            print(res.stdout[-500:] if res.stdout else res.stderr[-500:])
    finally:
        restore_pyproject(original_pyproject)

    # 6. Report stats
    if not meta_path.exists():
        print(f"  ❌ No meta output generated for {source_path_str}!")
        return {"total": 0, "killed": 0, "survived": 0}

    data = json.loads(meta_path.read_text(encoding="utf-8"))
    exit_codes = data.get("exit_code_by_key", {})
    killed = sum(1 for c in exit_codes.values() if c in (1, 2, 3, 37))
    survived = sum(1 for c in exit_codes.values() if c == 0)
    no_tests = sum(1 for c in exit_codes.values() if c in (None, 5, 33, 34))
    total = len(exit_codes)
    rate = (killed / total * 100) if total else 0.0

    status_icon = "🎉" if survived == 0 and total > 0 else "⚠️"
    print(
        f"\n  {status_icon} RESULT: Total={total} | Killed={killed} ({rate:.1f}%) | Survived={survived} | NoTests={no_tests}"
    )

    if show_survivors and survived > 0:
        survived_keys = [k for k, v in exit_codes.items() if v == 0]
        print(f"\n  🔍 SURVIVING MUTANT DIFFS ({len(survived_keys)}):")
        for k in survived_keys:
            diff_proc = subprocess.run(
                ["uv", "run", "mutmut", "show", k],
                capture_output=True,
                text=True,
                check=False,
            )
            print(diff_proc.stdout)

    return {"total": total, "killed": killed, "survived": survived}


def main() -> int:
    parser = argparse.ArgumentParser(description="SOTA Mutation Sweeper for Cresmo.")
    parser.add_argument("--file", type=str, help="Single file to mutate.")
    parser.add_argument("--wave", choices=["domain", "pipeline", "use_cases", "infra", "all"], help="Execution wave.")
    parser.add_argument("--no-reset", action="store_true", help="Do not reset mutant statuses.")
    parser.add_argument("--show-survivors", action="store_true", help="Print diff of surviving mutants.")
    args = parser.parse_args()

    reset = not args.no_reset

    if args.file:
        targets = [args.file]
    elif args.wave:
        if args.wave == "all":
            targets = [f for wave_files in WAVE_DEFINITIONS.values() for f in wave_files]
        else:
            targets = WAVE_DEFINITIONS[args.wave]
    else:
        parser.print_help()
        return 1

    totals = {"total": 0, "killed": 0, "survived": 0}
    for target in targets:
        res = run_mutation_on_module(target, reset=reset, show_survivors=args.show_survivors)
        totals["total"] += res["total"]
        totals["killed"] += res["killed"]
        totals["survived"] += res["survived"]

    rate = (totals["killed"] / totals["total"] * 100) if totals["total"] else 0.0
    print("\n" + "=" * 80)
    print(f"🏁 WAVE EXECUTION COMPLETE")
    print(f"   Total Mutants:   {totals['total']}")
    print(f"   Killed:          {totals['killed']} ({rate:.1f}%)")
    print(f"   Survived:        {totals['survived']}")
    print("=" * 80 + "\n")

    return 0 if totals["survived"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
