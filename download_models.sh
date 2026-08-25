#!/usr/bin/env bash
# download_models.sh — download LongCat model snapshots into a network-mounted directory
# Usage: ./download_models.sh /path/to/volume
# If no path provided, defaults to /runpod-volume/longcat-models
set -euo pipefail

TARGET=${1:-/runpod-volume/longcat-models}
HF_TOKEN=${HUGGINGFACE_HUB_TOKEN:-}

echo "Target model directory: $TARGET"
mkdir -p "$TARGET"

# Ensure huggingface_hub is available
if ! python3 -c "import huggingface_hub" >/dev/null 2>&1; then
  echo "Installing huggingface_hub (requires internet / pip)..."
  python3 -m pip install --upgrade pip setuptools wheel
  python3 -m pip install huggingface_hub
fi

# Export token if provided
if [ -n "${HF_TOKEN:-}" ]; then
  export HUGGINGFACE_HUB_TOKEN="$HF_TOKEN"
  echo "Using provided HUGGINGFACE_HUB_TOKEN"
else
  echo "No HUGGINGFACE_HUB_TOKEN provided; downloading public assets anonymously"
fi

export TARGET_DIR="$TARGET"

python3 - <<'PY'
import os
from pathlib import Path
from huggingface_hub import snapshot_download

target = Path(os.environ.get("TARGET_DIR", "/runpod-volume/longcat-models"))
target.mkdir(parents=True, exist_ok=True)

def snapshot(repo_id, local_subdir, **kwargs):
    local_dir = target / local_subdir
    print(f"-> snapshot_download({repo_id!r}) -> {local_dir}")
    # snapshot_download reuses existing files in local_dir; it only fetches missing/updated files
    snapshot_download(repo_id, local_dir=local_dir, **kwargs)
    print(f"   done: {local_dir}")

# Download minimal parts of base repo (only tokenizer, text_encoder, vae)
snapshot(
    "meituan-longcat/LongCat-Video",
    "LongCat-Video",
    allow_patterns=["tokenizer/*", "text_encoder/*", "vae/*"],
)

# Download Avatar checkpoint repo, skipping large assets we don't need
snapshot(
    "meituan-longcat/LongCat-Video-Avatar-1.5",
    "LongCat-Video-Avatar-1.5",
    ignore_patterns=[
        "assets/*",
        "base_model/*",
        "whisper-large-v3/flax_model.msgpack",
        "whisper-large-v3/*fp32*",
        "whisper-large-v3/*.bin",
    ],
)

print("All snapshots completed.")
PY

echo "All done. Models are under: $TARGET/LongCat-Video and $TARGET/LongCat-Video-Avatar-1.5"
