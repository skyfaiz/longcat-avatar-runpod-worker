from __future__ import annotations

import os
from pathlib import Path

from huggingface_hub import snapshot_download


root = Path(os.environ.get("LONGCAT_MODEL_ROOT", "/runpod-volume/models"))
root.mkdir(parents=True, exist_ok=True)

snapshot_download(
    "meituan-longcat/LongCat-Video",
    local_dir=root / "LongCat-Video",
    allow_patterns=["tokenizer/*", "text_encoder/*", "vae/*"],
)
snapshot_download(
    "meituan-longcat/LongCat-Video-Avatar-1.5",
    local_dir=root / "LongCat-Video-Avatar-1.5",
    ignore_patterns=[
        "assets/*",
        "base_model/*",
        "whisper-large-v3/flax_model.msgpack",
        "whisper-large-v3/*fp32*",
        "whisper-large-v3/*.bin",
    ],
)
