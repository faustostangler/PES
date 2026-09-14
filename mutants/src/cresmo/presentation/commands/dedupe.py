"""Command handler for cresmo dedupe."""

from __future__ import annotations

import argparse
import sys

from cresmo.presentation.composition import build_unify_duplicates_use_case
from cresmo.presentation.exit_codes import (
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_register_subparser__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_register_subparser__mutmut)
def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = subparsers.add_parser(
        "dedupe",
        help="Execute Stage 7 graph entity resolution, non-destructive merging, and link rewriting",
    )
    dedupe_parser.set_defaults(handler=handle_dedupe)


def x_register_subparser__mutmut_orig(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = subparsers.add_parser(
        "dedupe",
        help="Execute Stage 7 graph entity resolution, non-destructive merging, and link rewriting",
    )
    dedupe_parser.set_defaults(handler=handle_dedupe)


def x_register_subparser__mutmut_1(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = None
    dedupe_parser.set_defaults(handler=handle_dedupe)


def x_register_subparser__mutmut_2(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = subparsers.add_parser(
        None,
        help="Execute Stage 7 graph entity resolution, non-destructive merging, and link rewriting",
    )
    dedupe_parser.set_defaults(handler=handle_dedupe)


def x_register_subparser__mutmut_3(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = subparsers.add_parser(
        "dedupe",
        help=None,
    )
    dedupe_parser.set_defaults(handler=handle_dedupe)


def x_register_subparser__mutmut_4(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = subparsers.add_parser(
        help="Execute Stage 7 graph entity resolution, non-destructive merging, and link rewriting",
    )
    dedupe_parser.set_defaults(handler=handle_dedupe)


def x_register_subparser__mutmut_5(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = subparsers.add_parser(
        "dedupe",
        )
    dedupe_parser.set_defaults(handler=handle_dedupe)


def x_register_subparser__mutmut_6(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = subparsers.add_parser(
        "XXdedupeXX",
        help="Execute Stage 7 graph entity resolution, non-destructive merging, and link rewriting",
    )
    dedupe_parser.set_defaults(handler=handle_dedupe)


def x_register_subparser__mutmut_7(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = subparsers.add_parser(
        "DEDUPE",
        help="Execute Stage 7 graph entity resolution, non-destructive merging, and link rewriting",
    )
    dedupe_parser.set_defaults(handler=handle_dedupe)


def x_register_subparser__mutmut_8(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = subparsers.add_parser(
        "dedupe",
        help="XXExecute Stage 7 graph entity resolution, non-destructive merging, and link rewritingXX",
    )
    dedupe_parser.set_defaults(handler=handle_dedupe)


def x_register_subparser__mutmut_9(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = subparsers.add_parser(
        "dedupe",
        help="execute stage 7 graph entity resolution, non-destructive merging, and link rewriting",
    )
    dedupe_parser.set_defaults(handler=handle_dedupe)


def x_register_subparser__mutmut_10(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = subparsers.add_parser(
        "dedupe",
        help="EXECUTE STAGE 7 GRAPH ENTITY RESOLUTION, NON-DESTRUCTIVE MERGING, AND LINK REWRITING",
    )
    dedupe_parser.set_defaults(handler=handle_dedupe)


def x_register_subparser__mutmut_11(subparsers: argparse._SubParsersAction) -> None:
    """Register 'dedupe' subcommand parser."""
    dedupe_parser = subparsers.add_parser(
        "dedupe",
        help="Execute Stage 7 graph entity resolution, non-destructive merging, and link rewriting",
    )
    dedupe_parser.set_defaults(handler=None)

mutants_x_register_subparser__mutmut['_mutmut_orig'] = x_register_subparser__mutmut_orig # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_1'] = x_register_subparser__mutmut_1 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_2'] = x_register_subparser__mutmut_2 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_3'] = x_register_subparser__mutmut_3 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_4'] = x_register_subparser__mutmut_4 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_5'] = x_register_subparser__mutmut_5 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_6'] = x_register_subparser__mutmut_6 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_7'] = x_register_subparser__mutmut_7 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_8'] = x_register_subparser__mutmut_8 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_9'] = x_register_subparser__mutmut_9 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_10'] = x_register_subparser__mutmut_10 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_11'] = x_register_subparser__mutmut_11 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_handle_dedupe__mutmut)
def handle_dedupe(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write("Vault Graph Deduplication Summary:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_orig(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write("Vault Graph Deduplication Summary:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_1(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = None
        report = use_case.execute()
        sys.stdout.write("Vault Graph Deduplication Summary:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_2(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = None
        sys.stdout.write("Vault Graph Deduplication Summary:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_3(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write(None)
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_4(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write("XXVault Graph Deduplication Summary:\nXX")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_5(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write("vault graph deduplication summary:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_6(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write("VAULT GRAPH DEDUPLICATION SUMMARY:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_7(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write("Vault Graph Deduplication Summary:\n")
        sys.stdout.write(None)
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_8(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write("Vault Graph Deduplication Summary:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(None)
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_9(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write("Vault Graph Deduplication Summary:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = None
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_10(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write("Vault Graph Deduplication Summary:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(None)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_11(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write("Vault Graph Deduplication Summary:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = "XX, XX".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_12(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write("Vault Graph Deduplication Summary:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                None
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Deduplication error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_dedupe__mutmut_13(args: argparse.Namespace) -> int:
    """Unify duplicate atomic notes across the Obsidian vault graph."""
    try:
        use_case = build_unify_duplicates_use_case()
        report = use_case.execute()
        sys.stdout.write("Vault Graph Deduplication Summary:\n")
        sys.stdout.write(f"- Duplicate Clusters Unified: {report.duplicates_unified_count}\n")
        sys.stdout.write(f"- Total Inbound WikiLinks Rewritten: {report.total_links_rewritten}\n")
        for cluster in report.clusters:
            merged_str = ", ".join(f"[[{t.value}]]" for t in cluster.merged_titles)
            sys.stdout.write(
                f"  • Unified into [[{cluster.canonical_title.value}]]: {merged_str} "
                f"({cluster.links_rewritten_count} links rewritten)\n"
            )
        return EXIT_SUCCESS
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(None)
        return EXIT_INTERNAL_ERROR

mutants_x_handle_dedupe__mutmut['_mutmut_orig'] = x_handle_dedupe__mutmut_orig # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_1'] = x_handle_dedupe__mutmut_1 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_2'] = x_handle_dedupe__mutmut_2 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_3'] = x_handle_dedupe__mutmut_3 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_4'] = x_handle_dedupe__mutmut_4 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_5'] = x_handle_dedupe__mutmut_5 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_6'] = x_handle_dedupe__mutmut_6 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_7'] = x_handle_dedupe__mutmut_7 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_8'] = x_handle_dedupe__mutmut_8 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_9'] = x_handle_dedupe__mutmut_9 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_10'] = x_handle_dedupe__mutmut_10 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_11'] = x_handle_dedupe__mutmut_11 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_12'] = x_handle_dedupe__mutmut_12 # type: ignore # mutmut generated
mutants_x_handle_dedupe__mutmut['x_handle_dedupe__mutmut_13'] = x_handle_dedupe__mutmut_13 # type: ignore # mutmut generated
