"""Presentation command handlers for Cresmo CLI subcommands."""

from __future__ import annotations

from cresmo.presentation.commands.check_config import check_config, handle_check_config
from cresmo.presentation.commands.concat_master import concat_master, handle_concat_master
from cresmo.presentation.commands.dedupe import dedupe, handle_dedupe
from cresmo.presentation.commands.export_cookies import (
    export_cookies,
    handle_export_cookies,
)
from cresmo.presentation.commands.run import (
    execute_batch_dry_run,
    execute_batch_run,
    execute_single_video_run,
    handle_run,
    load_batch_sources,
    run,
)
from cresmo.presentation.commands.seed_prompts import handle_seed_prompts, seed_prompts
from cresmo.presentation.commands.sync import handle_sync, sync
from cresmo.presentation.commands.worker import handle_worker, worker

__all__ = [
    "check_config",
    "concat_master",
    "dedupe",
    "execute_batch_dry_run",
    "execute_batch_run",
    "execute_single_video_run",
    "export_cookies",
    "handle_check_config",
    "handle_concat_master",
    "handle_dedupe",
    "handle_export_cookies",
    "handle_run",
    "handle_seed_prompts",
    "handle_sync",
    "handle_worker",
    "load_batch_sources",
    "run",
    "seed_prompts",
    "sync",
    "worker",
]
