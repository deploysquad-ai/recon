#!/usr/bin/env bash
# Fresh install integration test.
# Clears the uvx cache and runs integration tests using the PyPI package.
#
# Usage:
#   ./tests/run_fresh_install_test.sh          # test against latest PyPI release
#   ./tests/run_fresh_install_test.sh --local   # test against local editable install
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RECON_CORE_DIR="$(dirname "$SCRIPT_DIR")"

if [[ "${1:-}" == "--local" ]]; then
    echo "==> Running integration tests against LOCAL install"
    cd "$RECON_CORE_DIR"
    .venv/bin/python -m pytest tests/test_integration_fresh.py -v
    exit $?
fi

echo "==> Clearing uvx cache for deploysquad-recon-core..."
uv cache clean deploysquad-recon-core 2>/dev/null || true

echo "==> Running integration tests against PyPI package..."
cd "$RECON_CORE_DIR"

# Use uv run with --with to pull from PyPI into a temp env
uv run \
    --python 3.12 \
    --with "deploysquad-recon-core" \
    --with "pytest>=8.0" \
    python -m pytest tests/test_integration_fresh.py -v

echo ""
echo "==> All integration tests passed against fresh PyPI install."
