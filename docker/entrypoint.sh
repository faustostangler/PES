#!/bin/sh
set -eu

# Ensure application virtualenv is first in PATH
export PATH="/app/.venv/bin:$PATH"

# Set default 12-Factor storage mounts
export DATA_DIR="${DATA_DIR:-/app/data}"
export VAULT_DIR="${VAULT_DIR:-/app/vault}"

ROLE="${ROLE:-cli}"

# If first argument matches a known cresmo CLI subcommand or option flag, run cresmo.
# When a specialized ROLE (e.g. worker, api) is set, ignore default Dockerfile CMD "check-config".
if [ "$#" -gt 0 ]; then
    if [ "$1" != "check-config" ] || [ "$ROLE" = "cli" ]; then
        case "$1" in
            check-config|run|sync|worker|dedupe|export-cookies|concat-master|seed-prompts|--help|-h|--version|-v)
                exec cresmo "$@"
                ;;
            cresmo)
                shift
                exec cresmo "$@"
                ;;
        esac
    fi
fi

# Route execution according to ROLE environment variable
case "$ROLE" in
    cli)
        if [ "$#" -eq 0 ]; then
            exec cresmo --help
        else
            exec cresmo "$@"
        fi
        ;;
    worker)
        echo "[Cresmo 12-Factor Container] Starting worker daemon..."
        exec cresmo sync
        ;;
    api)
        echo "[Cresmo 12-Factor Container] Starting API server on port ${PORT:-8000}..."
        exec uvicorn cresmo.presentation.api:app --host 0.0.0.0 --port "${PORT:-8000}"
        ;;
    *)
        exec "$@"
        ;;
esac

