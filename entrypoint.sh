#!/usr/bin/env bash
set -euo pipefail

python /opt/worker/sync_models.py
exec python -u /opt/worker/handler.py
