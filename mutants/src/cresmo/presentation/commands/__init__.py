"""Presentation command handlers for Cresmo CLI subcommands."""

from __future__ import annotations

from cresmo.presentation.commands import (
    check_config,
    dedupe,
    run,
    sync,
    worker,
)
from cresmo.presentation.commands.check_config import handle_check_config
from cresmo.presentation.commands.dedupe import handle_dedupe
from cresmo.presentation.commands.run import (
    execute_batch_dry_run,
    execute_batch_run,
    execute_single_video_run,
    handle_run,
    load_batch_sources,
)
from cresmo.presentation.commands.sync import handle_sync
from cresmo.presentation.commands.worker import handle_worker

__all__ = [
    "check_config",
    "dedupe",
    "execute_batch_dry_run",
    "execute_batch_run",
    "execute_single_video_run",
    "handle_check_config",
    "handle_dedupe",
    "handle_run",
    "handle_sync",
    "handle_worker",
    "load_batch_sources",
    "run",
    "sync",
    "worker",
]


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
