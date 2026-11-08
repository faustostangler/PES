"""Presentation command handlers for Cresmo CLI subcommands.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-026: Clean Code Anti-Patterns & Code Smell Governance
    - ADR-053: Lazy Presentation CLI Loading, Subcommand Decoupling, and Default-Fast Ingestion
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from cresmo.presentation.commands.check_config import (
        check_config as check_config,
    )
    from cresmo.presentation.commands.check_config import (
        handle_check_config as handle_check_config,
    )
    from cresmo.presentation.commands.concat_master import (
        concat_master as concat_master,
    )
    from cresmo.presentation.commands.concat_master import (
        handle_concat_master as handle_concat_master,
    )
    from cresmo.presentation.commands.dedupe import (
        dedupe as dedupe,
    )
    from cresmo.presentation.commands.dedupe import (
        handle_dedupe as handle_dedupe,
    )
    from cresmo.presentation.commands.export_cookies import (
        export_cookies as export_cookies,
    )
    from cresmo.presentation.commands.export_cookies import (
        handle_export_cookies as handle_export_cookies,
    )
    from cresmo.presentation.commands.run import (
        execute_batch_dry_run as execute_batch_dry_run,
    )
    from cresmo.presentation.commands.run import (
        execute_batch_run as execute_batch_run,
    )
    from cresmo.presentation.commands.run import (
        execute_single_video_run as execute_single_video_run,
    )
    from cresmo.presentation.commands.run import (
        handle_run as handle_run,
    )
    from cresmo.presentation.commands.run import (
        load_batch_sources as load_batch_sources,
    )
    from cresmo.presentation.commands.run import (
        run as run,
    )
    from cresmo.presentation.commands.seed_prompts import (
        handle_seed_prompts as handle_seed_prompts,
    )
    from cresmo.presentation.commands.seed_prompts import (
        seed_prompts as seed_prompts,
    )
    from cresmo.presentation.commands.sync import (
        handle_sync as handle_sync,
    )
    from cresmo.presentation.commands.sync import (
        sync as sync,
    )
    from cresmo.presentation.commands.worker import (
        handle_worker as handle_worker,
    )
    from cresmo.presentation.commands.worker import (
        worker as worker,
    )

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

_SYMBOL_TO_MODULE: dict[str, str] = {
    "check_config": "cresmo.presentation.commands.check_config",
    "handle_check_config": "cresmo.presentation.commands.check_config",
    "concat_master": "cresmo.presentation.commands.concat_master",
    "handle_concat_master": "cresmo.presentation.commands.concat_master",
    "dedupe": "cresmo.presentation.commands.dedupe",
    "handle_dedupe": "cresmo.presentation.commands.dedupe",
    "export_cookies": "cresmo.presentation.commands.export_cookies",
    "handle_export_cookies": "cresmo.presentation.commands.export_cookies",
    "run": "cresmo.presentation.commands.run",
    "handle_run": "cresmo.presentation.commands.run",
    "execute_batch_dry_run": "cresmo.presentation.commands.run",
    "execute_batch_run": "cresmo.presentation.commands.run",
    "execute_single_video_run": "cresmo.presentation.commands.run",
    "load_batch_sources": "cresmo.presentation.commands.run",
    "seed_prompts": "cresmo.presentation.commands.seed_prompts",
    "handle_seed_prompts": "cresmo.presentation.commands.seed_prompts",
    "sync": "cresmo.presentation.commands.sync",
    "handle_sync": "cresmo.presentation.commands.sync",
    "worker": "cresmo.presentation.commands.worker",
    "handle_worker": "cresmo.presentation.commands.worker",
}


def __getattr__(name: str) -> Any:
    """Lazily import and resolve command symbols on demand per PEP 562 and ADR-053."""
    mod_path = _SYMBOL_TO_MODULE.get(name)
    if mod_path is not None:
        mod = importlib.import_module(mod_path)
        attr = getattr(mod, name)
        globals()[name] = attr
        return attr
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """Return all public exportable symbols alongside module globals."""
    return sorted(list(globals().keys()) + __all__)
