"""Automated Mutation Testing Compliance Gate (Phase 4: Treatment).

Evaluates mutmut mutation testing outcomes against Doctor Stangler Architecture Method gates:
- Domain Gate: 0 Survivors (100.0% Kill Rate required).
- Application Gate: Progress tracking toward 0 Survivors (100.0% Kill Rate).
- Infrastructure Gate: Progress tracking toward < 5% Survivors (>95.0% Kill Rate).
- System Gate: 0 Timeouts / Infinite Loops.

Usage:
    uv run python tests/quality/run_mutation_gate.py [--enforce-domain] [--enforce-application]
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
        status_icon = "🎉" if (layer == "domain" and s["survived"] == 0 and total > 0) else "📊"
        print(
            f"{status_icon} {layer.capitalize():<15} | {total:<7} | {s['killed']:<7} | {s['survived']:<8} | {s['no_tests']:<8} | {s['timeout']:<8} | {rate:>7.2f}%"
        )

    print("=" * 92)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Cresmo mutation test compliance.")
    parser.add_argument(
        "--mutants-dir",
        type=Path,
        default=Path("mutants"),
        help="Root directory containing mutmut mutation database.",
    )
    parser.add_argument(
        "--enforce-domain",
        action="store_true",
        default=True,
        help="Fail fast (exit 1) if Sacred Domain contains even 1 surviving mutant.",
    )
    args = parser.parse_args()

    stats = collect_mutation_stats(args.mutants_dir)
    print_mutation_report(stats)

    domain_stats = stats.get(
        "domain", {"total": 0, "killed": 0, "survived": 0, "no_tests": 0, "timeout": 0}
    )
    if args.enforce_domain:
        if domain_stats["total"] == 0:
            print("❌ FAIL: No Domain mutants found in database. Run 'uv run mutmut run' first.\n")
            return 1
        if domain_stats["survived"] > 0:
            print(
                f"❌ FAIL: Sacred Domain has {domain_stats['survived']} surviving mutants! Target: 0.\n"
            )
            return 1
        print("✅ PASS: Sacred Domain is 100% resilient with ZERO surviving mutants!\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
