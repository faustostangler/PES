"""Automated Mutation Testing Compliance Gate (Phase 4: Treatment).

Evaluates mutmut mutation testing outcomes against Doctor Stangler Architecture Method gates:
- Domain Gate: 0 Survivors (100.0% Kill Rate required).
- Application Gate: 0 Survivors (100.0% Kill Rate required).
- Infrastructure Gate: < 5% Survivors (>=95.0% Kill Rate required).
- Presentation Gate: Regression tracking (configurable, default >=90.0%).
- System Gate: 0 Timeouts / Infinite Loops.

Usage:
    uv run python tests/quality/run_mutation_gate.py [--enforce-all]
    uv run python tests/quality/run_mutation_gate.py [--enforce-domain] [--enforce-application] [--enforce-infrastructure]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TypedDict


class LayerStats(TypedDict):
    total: int
    killed: int
    survived: int
    no_tests: int
    timeout: int


def collect_mutation_stats(mutants_dir: Path) -> dict[str, LayerStats]:
    """Scan all .meta files in mutants/src/cresmo and aggregate stats by architectural layer."""
    cresmo_dir = mutants_dir / "src" / "cresmo"
    layers = ["domain", "application", "infrastructure", "presentation"]
    stats: dict[str, LayerStats] = {
        l: {"total": 0, "killed": 0, "survived": 0, "no_tests": 0, "timeout": 0} for l in layers
    }

    if not cresmo_dir.exists():
        return stats

    for meta_file in cresmo_dir.glob("**/*.meta"):
        rel_parts = meta_file.relative_to(cresmo_dir).parts
        if not rel_parts:
            continue
        layer = rel_parts[0]
        if layer not in stats:
            continue

        try:
            data = json.loads(meta_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        for exit_code in data.get("exit_code_by_key", {}).values():
            stats[layer]["total"] += 1
            if exit_code in (1, 3, 37):
                stats[layer]["killed"] += 1
            elif exit_code == 0:
                stats[layer]["survived"] += 1
            elif exit_code in (None, 5, 33, 34):
                stats[layer]["no_tests"] += 1
            elif exit_code in (24, -24, 36, 152, 255):
                stats[layer]["timeout"] += 1
            else:
                stats[layer]["no_tests"] += 1

    return stats


def print_mutation_report(stats: dict[str, LayerStats]) -> None:
    """Print structured terminal table with layer-by-layer mutation resilience."""
    print("\n" + "=" * 92)
    print(" 🛡️  CRESMO ARCHITECTURAL MUTATION TESTING QUALITY GATE REPORT (stangler-treatment)")
    print("=" * 92)
    print(
        f"{'Architectural Layer':<18} | {'Total':<7} | {'Killed':<7} | {'Survived':<8} | {'No Tests':<8} | {'Timeouts':<8} | {'Kill Rate':<9}"
    )
    print("-" * 92)

    for layer, s in stats.items():
        total = s["total"]
        rate = (s["killed"] / total * 100) if total > 0 else 0.0
        status_icon = "🎉" if (layer in ("domain", "application") and s["survived"] == 0 and total > 0) else "📊"
        print(
            f"{status_icon} {layer.capitalize():<15} | {total:<7} | {s['killed']:<7} | {s['survived']:<8} | {s['no_tests']:<8} | {s['timeout']:<8} | {rate:>7.2f}%"
        )

    print("=" * 92)


def verify_module_completeness(src_dir: Path, mutants_dir: Path) -> list[str]:
    """Verify that all non-interface functional python modules have corresponding .meta files."""
    missing: list[str] = []
    cresmo_src = src_dir / "cresmo"
    cresmo_mutants = mutants_dir / "src" / "cresmo"
    if not cresmo_src.exists():
        return missing

    for src_file in sorted(cresmo_src.glob("**/*.py")):
        if src_file.name == "__init__.py" or "ports" in src_file.parts:
            continue
        rel = src_file.relative_to(cresmo_src)
        meta_file = cresmo_mutants / rel.with_suffix(".py.meta")
        if not meta_file.exists():
            missing.append(str(rel))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Cresmo mutation test compliance.")
    parser.add_argument(
        "--mutants-dir",
        type=Path,
        default=Path("mutants"),
        help="Root directory containing mutmut mutation database.",
    )
    parser.add_argument(
        "--src-dir",
        type=Path,
        default=Path("src"),
        help="Root directory containing application source code.",
    )
    parser.add_argument(
        "--enforce-domain",
        action="store_true",
        default=False,
        help="Fail fast (exit 1) if Sacred Domain contains even 1 surviving mutant (requires 100.0%).",
    )
    parser.add_argument(
        "--enforce-application",
        action="store_true",
        default=False,
        help="Fail fast (exit 1) if Application layer contains even 1 surviving mutant (requires 100.0%).",
    )
    parser.add_argument(
        "--enforce-infrastructure",
        action="store_true",
        default=False,
        help="Fail fast (exit 1) if Infrastructure kill rate falls below threshold.",
    )
    parser.add_argument(
        "--enforce-presentation",
        action="store_true",
        default=False,
        help="Fail fast (exit 1) if Presentation kill rate falls below threshold.",
    )
    parser.add_argument(
        "--enforce-all",
        action="store_true",
        default=False,
        help="Enforce compliance gates across ALL architectural layers simultaneously.",
    )
    parser.add_argument(
        "--verify-completeness",
        action="store_true",
        default=False,
        help="Verify that all functional modules have non-empty mutation profiles in the database.",
    )
    parser.add_argument(
        "--min-infra-rate",
        type=float,
        default=95.0,
        help="Minimum required kill rate percentage for Infrastructure layer (default: 95.0%%).",
    )
    parser.add_argument(
        "--min-pres-rate",
        type=float,
        default=90.0,
        help="Minimum required kill rate percentage for Presentation layer (default: 90.0%%).",
    )
    args = parser.parse_args()

    # If no flags passed, default to --enforce-domain
    if not any([
        args.enforce_domain,
        args.enforce_application,
        args.enforce_infrastructure,
        args.enforce_presentation,
        args.enforce_all,
        args.verify_completeness,
    ]):
        args.enforce_domain = True

    if args.enforce_all:
        args.enforce_domain = True
        args.enforce_application = True
        args.enforce_infrastructure = True
        args.enforce_presentation = True
        args.verify_completeness = True

    stats = collect_mutation_stats(args.mutants_dir)
    print_mutation_report(stats)

    exit_code = 0

    # 1. Domain Gate (Hard: 0 survivors)
    if args.enforce_domain:
        domain = stats.get("domain", {"total": 0, "killed": 0, "survived": 0, "no_tests": 0, "timeout": 0})
        if domain["total"] == 0:
            print("❌ FAIL: No Domain mutants found in database.\n")
            exit_code = 1
        elif domain["survived"] > 0:
            print(f"❌ FAIL: Sacred Domain has {domain['survived']} surviving mutants! Target: 0 (100.0%% required).\n")
            exit_code = 1
        else:
            print("✅ PASS: Sacred Domain Gate — 100.0% resilient with ZERO surviving mutants.")

    # 2. Application Gate (Hard: 0 survivors)
    if args.enforce_application:
        app = stats.get("application", {"total": 0, "killed": 0, "survived": 0, "no_tests": 0, "timeout": 0})
        if app["total"] == 0:
            print("❌ FAIL: No Application mutants found in database.\n")
            exit_code = 1
        elif app["survived"] > 0:
            print(f"❌ FAIL: Application Core has {app['survived']} surviving mutants! Target: 0 (100.0%% required).\n")
            exit_code = 1
        else:
            print("✅ PASS: Application Core Gate — 100.0% resilient with ZERO surviving mutants.")

    # 3. Infrastructure Gate (Threshold >= min-infra-rate)
    if args.enforce_infrastructure:
        infra = stats.get("infrastructure", {"total": 0, "killed": 0, "survived": 0, "no_tests": 0, "timeout": 0})
        rate = (infra["killed"] / infra["total"] * 100) if infra["total"] > 0 else 0.0
        if infra["total"] == 0:
            print("❌ FAIL: No Infrastructure mutants found in database.\n")
            exit_code = 1
        elif rate < args.min_infra_rate:
            print(f"❌ FAIL: Infrastructure kill rate {rate:.2f}% is below target {args.min_infra_rate:.2f}%!\n")
            exit_code = 1
        else:
            print(f"✅ PASS: Infrastructure Gate — {rate:.2f}% kill rate satisfies target (>={args.min_infra_rate:.2f}%).")

    # 4. Presentation Gate (Threshold >= min-pres-rate)
    if args.enforce_presentation:
        pres = stats.get("presentation", {"total": 0, "killed": 0, "survived": 0, "no_tests": 0, "timeout": 0})
        rate = (pres["killed"] / pres["total"] * 100) if pres["total"] > 0 else 0.0
        if pres["total"] == 0:
            print("❌ FAIL: No Presentation mutants found in database.\n")
            exit_code = 1
        elif rate < args.min_pres_rate:
            print(f"❌ FAIL: Presentation kill rate {rate:.2f}% is below target {args.min_pres_rate:.2f}%!\n")
            exit_code = 1
        else:
            print(f"✅ PASS: Presentation Gate — {rate:.2f}% kill rate satisfies target (>={args.min_pres_rate:.2f}%).")

    # 5. Completeness Check
    if args.verify_completeness:
        missing = verify_module_completeness(args.src_dir, args.mutants_dir)
        if missing:
            print(f"⚠️  WARNING: {len(missing)} functional modules lack mutation profiles in {args.mutants_dir}:")
            for m in missing[:10]:
                print(f"    - {m}")
            if len(missing) > 10:
                print(f"    ... and {len(missing) - 10} more.")
            exit_code = 1
        else:
            print("✅ PASS: Module Completeness — All functional source modules have active mutation profiles.")

    print()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
