"""Cresmo Command-Line Interface (CLI) Entrypoint.

Follows the Humble Object pattern per Clean/Hexagonal Architecture.
Responsible solely for Typer argument parsing, subcommand routing, and exit code propagation.
All domain workflows and command options reside in isolated command modules.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-042: Modern Typer Presentation CLI Driving Adapter
    - SPEC-002: CLI Controller & Exit Codes
    - SPEC-042: Modern Typer Presentation CLI Specifications
"""

from __future__ import annotations

import importlib
import sys
from collections.abc import Sequence
from typing import Any

import click
import typer
from typer.core import TyperCommand, TyperGroup

from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)

__all__ = [
    "app",
    "main",
]

_LAZY_COMMANDS: dict[str, tuple[str, str, str]] = {
    "run": (
        "cresmo.presentation.commands.run",
        "run",
        "Run end-to-end knowledge synthesis for a video or manifest playlist",
    ),
    "check-config": (
        "cresmo.presentation.commands.check_config",
        "check_config",
        "Validate runtime environment, storage paths, and secrets fail-fast",
    ),
    "sync": (
        "cresmo.presentation.commands.sync",
        "sync",
        "Poll and synchronize video feeds from YouTube channels or playlists",
    ),
    "worker": (
        "cresmo.presentation.commands.worker",
        "worker",
        "Run continuous polling worker daemon with heartbeat health reporting",
    ),
    "dedupe": (
        "cresmo.presentation.commands.dedupe",
        "dedupe",
        "Execute graph entity resolution, non-destructive merging, and link rewriting",
    ),
    "export-cookies": (
        "cresmo.presentation.commands.export_cookies",
        "export_cookies",
        "Extract and validate YouTube authentication cookies from installed web browsers",
    ),
    "concat-master": (
        "cresmo.presentation.commands.concat_master",
        "concat_master",
        "Consolidate enriched compendiums in ascending chronological order into master RAG files",
    ),
    "seed-prompts": (
        "cresmo.presentation.commands.seed_prompts",
        "seed_prompts",
        "Synchronize canonical prompt templates into Langfuse prompt management",
    ),
}


class LazyCommand(TyperCommand):
    """Click Command wrapper executing on-demand dynamic module import per ADR-055."""

    def __init__(self, name: str, module_path: str, func_name: str, help_text: str) -> None:
        super().__init__(name=name, help=help_text)
        self.module_path = module_path
        self.func_name = func_name
        self._real_cmd: Any = None

    def _load_cmd(self) -> Any:
        if self._real_cmd is None:
            mod = importlib.import_module(self.module_path)
            func = getattr(mod, self.func_name)
            sub_app = typer.Typer()
            sub_app.command(name=self.name, help=self.help)(func)
            cmd = typer.main.get_command(sub_app)
            self._real_cmd = cmd
        assert self._real_cmd is not None
        return self._real_cmd

    def parse_args(self, ctx: Any, args: list[str]) -> list[str]:
        real_cmd = self._load_cmd()
        self.params = real_cmd.params
        res = real_cmd.parse_args(ctx, args)
        return list(res)

    def invoke(self, ctx: Any) -> Any:
        return self._load_cmd().invoke(ctx)

    def get_help(self, ctx: Any) -> str:
        return str(self._load_cmd().get_help(ctx))

    def format_help(self, ctx: Any, formatter: Any) -> None:
        self._load_cmd().format_help(ctx, formatter)


class LazyTyperGroup(TyperGroup):
    """Custom TyperGroup deferring subcommand module imports until explicit execution (ADR-055)."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for cmd_name, (mod_path, func_name, help_text) in _LAZY_COMMANDS.items():
            self.commands[cmd_name] = LazyCommand(cmd_name, mod_path, func_name, help_text)

    def list_commands(self, ctx: Any) -> list[str]:
        base_cmds = set(super().list_commands(ctx))
        return sorted(base_cmds.union(_LAZY_COMMANDS.keys()))

    def get_command(self, ctx: Any, cmd_name: str) -> Any:
        if cmd_name in _LAZY_COMMANDS:
            if cmd_name not in self.commands or not isinstance(
                self.commands[cmd_name], LazyCommand
            ):
                mod_path, func_name, help_text = _LAZY_COMMANDS[cmd_name]
                self.commands[cmd_name] = LazyCommand(cmd_name, mod_path, func_name, help_text)
            return self.commands[cmd_name]
        return super().get_command(ctx, cmd_name)


def _lazy_command_stub() -> None:
    """Empty callback stub to satisfy Typer command registration during inspection."""


app = typer.Typer(
    cls=LazyTyperGroup,
    name="cresmo",
    help="Cresmo Knowledge Synthesis",
    no_args_is_help=True,
    add_completion=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

for _cmd_name, (_, _, _help_text) in _LAZY_COMMANDS.items():
    app.registered_commands.append(
        typer.models.CommandInfo(
            name=_cmd_name,
            callback=_lazy_command_stub,
            help=_help_text,
        )
    )


@app.callback()
def _main_callback() -> None:
    """Cresmo Knowledge Synthesis root entrypoint."""


def main(argv: Sequence[str] | None = None) -> int:
    """Execute Cresmo command-line interface entrypoint.

    Conforms to SPEC-002, SPEC-042, and ADR-042: Humble Object CLI Controller
    with strictly segregated process exit codes.

    Args:
        argv: Optional sequence of command-line argument strings. If None, uses sys.argv[1:].

    Returns:
        Process exit code integer conforming to the exit code taxonomy in exit_codes.py.
    """
    try:
        exit_result = app(args=list(argv) if argv is not None else None, standalone_mode=False)
        return EXIT_SUCCESS if exit_result is None else int(exit_result)
    except typer.Exit as exc:
        return int(exc.exit_code)
    except click.exceptions.Exit as exc:
        return int(exc.exit_code)
    except typer.exceptions.TyperException as exc:
        code = getattr(exc, "exit_code", EXIT_CONFIG_OR_USAGE_ERROR)
        return int(code) if isinstance(code, int) else EXIT_CONFIG_OR_USAGE_ERROR
    except click.ClickException as exc:
        sys.stderr.write(f"Usage error: {exc}\n")
        code = getattr(exc, "exit_code", EXIT_CONFIG_OR_USAGE_ERROR)
        return int(code) if isinstance(code, int) else EXIT_CONFIG_OR_USAGE_ERROR
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    sys.exit(main())
