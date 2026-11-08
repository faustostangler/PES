"""Root pytest configuration and structlog bridge.

Configures structlog to dispatch through stdlib logging so pytest's caplog
fixture captures all structlog events during unit and integration test runs.
"""

from __future__ import annotations

import os

import structlog

# Ensure CLI invocations during test runs do not trigger host docker compose operations
os.environ.setdefault("CRESMO_SKIP_UP", "1")

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.render_to_log_kwargs,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=False,
)
