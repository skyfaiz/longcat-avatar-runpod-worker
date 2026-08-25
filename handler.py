from __future__ import annotations

import base64
import json
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import runpod


MODEL_ROOT = Path(os.environ.get("LONGCAT_MODEL_ROOT", "/runpod-volume/longcat-models"))
REPO = Path(os.environ.get("LONGCAT_REPO", "/opt/longcat"))
MAX_INPUT_BYTES = 25 * 1024 * 1024


def _materialize(value: str, target: Path) -> None:
    if value.startswith("data:"):
        try:
            data = base64.b64decode(value.split(",", 1)[1], validate=True)
        except (IndexError, ValueError) as exc:
            raise ValueError("Invalid data URI") from exc
    elif value.startswith(("https://", "http://")):
        request = urllib.request.Request(value, headers={"User-Agent": "longcat-runpod-worker/1"})
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read(MAX_INPUT_BYTES + 1)
    else:
        raise ValueError("Input must be an HTTP(S) URL or data URI")
    if not data or len(data) > MAX_INPUT_BYTES:
        raise ValueError("Input is empty or larger than 25 MB")
    target.write_bytes(data)


def _validated(job_input: dict) -> tuple[str, int, str]:
    prompt = str(job_input.get("prompt", "")).strip()
    segments = int(job_input.get("segments", 1))
    resolution = str(job_input.get("resolution", "480p"))
    if not prompt or len(prompt) > 2000:
        raise ValueError("prompt must contain 1-2000 characters")
    if not 1 <= segments <= 20:
        raise ValueError("segments must be between 1 and 20")
    if resolution not in {"480p", "720p"}:
        raise ValueError("resolution must be 480p or 720p")
    return prompt, segments, resolution


def handler(job: dict) -> dict:
    job_input = job.get("input") or {}
    prompt, segments, resolution = _validated(job_input)
    checkpoint = MODEL_ROOT / "LongCat-Video-Avatar-1.5"
    base_model = MODEL_ROOT / "LongCat-Video"
    if not checkpoint.is_dir() or not base_model.is_dir():
        raise RuntimeError(f"Models are missing under {MODEL_ROOT}")

    with tempfile.TemporaryDirectory(prefix="longcat-") as directory:
        work = Path(directory)
        image, audio, output = work / "portrait.png", work / "speech.wav", work / "output"
        output.mkdir()
        _materialize(str(job_input.get("image", "")), image)
        _materialize(str(job_input.get("audio", "")), audio)
        input_json = work / "input.json"
        input_json.write_text(
            json.dumps(
                {"prompt": prompt, "cond_image": str(image), "cond_audio": {"person1": str(audio)}},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        command = [
            "torchrun",
            "--nproc_per_node=1",
            "run_demo_avatar_single_audio_to_video.py",
            "--context_parallel_size=1",
            f"--checkpoint_dir={checkpoint}",
            "--stage_1=ai2v",
            f"--input_json={input_json}",
            f"--output_dir={output}",
            f"--resolution={resolution}",
            f"--num_segments={segments}",
            "--use_distill",
            "--model_type=avatar-v1.5",
            "--use_int8",
        ]
        subprocess.run(command, cwd=REPO, check=True)
        videos = sorted(output.glob("*.mp4"), key=lambda path: path.stat().st_mtime)
        if not videos:
            raise RuntimeError("LongCat finished without an MP4")
        video = videos[-1].read_bytes()
        return {
            "filename": "longcat-avatar.mp4",
            "mime_type": "video/mp4",
            "video_base64": base64.b64encode(video).decode(),
        }


runpod.serverless.start({"handler": handler})
