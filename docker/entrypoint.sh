#!/bin/sh
set -eu

# Ensure application virtualenv is first in PATH
export PATH="/app/.venv/bin:$PATH"

# Set default 12-Factor storage mounts
export DATA_DIR="${DATA_DIR:-/app/data}"
export VAULT_DIR="${VAULT_DIR:-/app/vault}"

# If first argument matches a known cresmo CLI subcommand or option flag, run cresmo
if [ "$#" -gt 0 ]; then
    case "$1" in
        check-config|run|sync|dedupe|--help|-h|--version|-v)
            exec cresmo "$@"
            ;;
        cresmo)
            shift
            exec cresmo "$@"
            ;;
    esac
fi

# Route execution according to ROLE environment variable
ROLE="${ROLE:-cli}"

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
        exec cresmo sync --all
        ;;
    api)
        echo "[Cresmo 12-Factor Container] Starting API server on port ${PORT:-8000}..."
        exec uvicorn cresmo.presentation.api:app --host 0.0.0.0 --port "${PORT:-8000}"
        ;;
    *)
        exec "$@"
        ;;
esac
