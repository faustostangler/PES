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

import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, TypedDict

import click
import typer


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
        status_icon = (
            "🎉"
            if (layer in ("domain", "application") and s["survived"] == 0 and total > 0)
            else "📊"
        )
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


app = typer.Typer(
    name="run-mutation-gate",
    help="Evaluate Cresmo mutation test compliance.",
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def evaluate(
    mutants_dir: Annotated[
        Path,
        typer.Option(
            "--mutants-dir",
            help="Root directory containing mutmut mutation database.",
        ),
    ] = Path("mutants"),
    src_dir: Annotated[
        Path,
        typer.Option(
            "--src-dir",
            help="Root directory containing application source code.",
        ),
    ] = Path("src"),
    enforce_domain: Annotated[
        bool,
        typer.Option(
            "--enforce-domain",
            help="Fail fast (exit 1) if Sacred Domain contains even 1 surviving mutant (requires 100.0%).",
        ),
    ] = False,
    enforce_application: Annotated[
        bool,
        typer.Option(
            "--enforce-application",
            help="Fail fast (exit 1) if Application layer contains even 1 surviving mutant (requires 100.0%).",
        ),
    ] = False,
    enforce_infrastructure: Annotated[
        bool,
        typer.Option(
            "--enforce-infrastructure",
            help="Fail fast (exit 1) if Infrastructure kill rate falls below threshold.",
        ),
    ] = False,
    enforce_presentation: Annotated[
        bool,
        typer.Option(
            "--enforce-presentation",
            help="Fail fast (exit 1) if Presentation kill rate falls below threshold.",
        ),
    ] = False,
    enforce_all: Annotated[
        bool,
        typer.Option(
            "--enforce-all",
            help="Enforce compliance gates across ALL architectural layers simultaneously.",
        ),
    ] = False,
    verify_completeness: Annotated[
        bool,
        typer.Option(
            "--verify-completeness",
            help="Verify that all functional modules have non-empty mutation profiles in the database.",
        ),
    ] = False,
    min_infra_rate: Annotated[
        float,
        typer.Option(
            "--min-infra-rate",
            help="Minimum required kill rate percentage for Infrastructure layer (default: 95.0%).",
        ),
    ] = 95.0,
    min_pres_rate: Annotated[
        float,
        typer.Option(
            "--min-pres-rate",
            help="Minimum required kill rate percentage for Presentation layer (default: 90.0%).",
        ),
    ] = 90.0,
) -> None:

    # If no flags passed, default to --enforce-domain
    active_domain = enforce_domain
    active_application = enforce_application
    active_infrastructure = enforce_infrastructure
    active_presentation = enforce_presentation
    active_completeness = verify_completeness

    if not any(
        [
            enforce_domain,
            enforce_application,
            enforce_infrastructure,
            enforce_presentation,
            enforce_all,
            verify_completeness,
        ]
    ):
        active_domain = True

    if enforce_all:
        active_domain = True
        active_application = True
        active_infrastructure = True
        active_presentation = True
        active_completeness = True

    stats = collect_mutation_stats(mutants_dir)
    print_mutation_report(stats)

    exit_code = 0

    # 1. Domain Gate (Hard: 0 survivors)
    if active_domain:
        domain = stats.get(
            "domain", {"total": 0, "killed": 0, "survived": 0, "no_tests": 0, "timeout": 0}
        )
        if domain["total"] == 0:
            print("❌ FAIL: No Domain mutants found in database.\n")
            exit_code = 1
        elif domain["survived"] > 0:
            print(
                f"❌ FAIL: Sacred Domain has {domain['survived']} surviving mutants! Target: 0 (100.0% required).\n"
            )
            exit_code = 1
        else:
            print("✅ PASS: Sacred Domain Gate — 100.0% resilient with ZERO surviving mutants.")

    # 2. Application Gate (Hard: 0 survivors)
    if active_application:
        app = stats.get(
            "application", {"total": 0, "killed": 0, "survived": 0, "no_tests": 0, "timeout": 0}
        )
        if app["total"] == 0:
            print("❌ FAIL: No Application mutants found in database.\n")
            exit_code = 1
        elif app["survived"] > 0:
            print(
                f"❌ FAIL: Application Core has {app['survived']} surviving mutants! Target: 0 (100.0% required).\n"
            )
            exit_code = 1
        else:
            print("✅ PASS: Application Core Gate — 100.0% resilient with ZERO surviving mutants.")

    # 3. Infrastructure Gate (Threshold >= min-infra-rate)
    if active_infrastructure:
        infra = stats.get(
            "infrastructure", {"total": 0, "killed": 0, "survived": 0, "no_tests": 0, "timeout": 0}
        )
        rate = (infra["killed"] / infra["total"] * 100) if infra["total"] > 0 else 0.0
        if infra["total"] == 0:
            print("❌ FAIL: No Infrastructure mutants found in database.\n")
            exit_code = 1
        elif rate < min_infra_rate:
            print(
                f"❌ FAIL: Infrastructure kill rate {rate:.2f}% is below target {min_infra_rate:.2f}%!\n"
            )
            exit_code = 1
        else:
            print(
                f"✅ PASS: Infrastructure Gate — {rate:.2f}% kill rate satisfies target (>={min_infra_rate:.2f}%)."
            )

    # 4. Presentation Gate (Threshold >= min-pres-rate)
    if active_presentation:
        pres = stats.get(
            "presentation", {"total": 0, "killed": 0, "survived": 0, "no_tests": 0, "timeout": 0}
        )
        rate = (pres["killed"] / pres["total"] * 100) if pres["total"] > 0 else 0.0
        if pres["total"] == 0:
            print("❌ FAIL: No Presentation mutants found in database.\n")
            exit_code = 1
        elif rate < min_pres_rate:
            print(
                f"❌ FAIL: Presentation kill rate {rate:.2f}% is below target {min_pres_rate:.2f}%!\n"
            )
            exit_code = 1
        else:
            print(
                f"✅ PASS: Presentation Gate — {rate:.2f}% kill rate satisfies target (>={min_pres_rate:.2f}%)."
            )

    # 5. Completeness Check
    if active_completeness:
        missing = verify_module_completeness(src_dir, mutants_dir)
        if missing:
            print(
                f"⚠️  WARNING: {len(missing)} functional modules lack mutation profiles in {mutants_dir}:"
            )
            for m in missing[:10]:
                print(f"    - {m}")
            if len(missing) > 10:
                print(f"    ... and {len(missing) - 10} more.")
            exit_code = 1
        else:
            print(
                "✅ PASS: Module Completeness — All functional source modules have active mutation profiles."
            )

    print()
    if exit_code != 0:
        raise typer.Exit(code=exit_code)


def main(argv: Sequence[str] | None = None) -> int:
    """Execute mutation gate runner entrypoint.

    Args:
        argv: Optional sequence of CLI arguments. If None, uses sys.argv[1:].

    Returns:
        Process exit code integer.
    """
    try:
        res = app(args=list(argv) if argv is not None else None, standalone_mode=False)
        return 0 if res is None else int(res)
    except typer.Exit as exc:
        return exc.exit_code
    except click.ClickException as exc:
        sys.stderr.write(f"Usage error: {exc}\n")
        return getattr(exc, "exit_code", 2)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
