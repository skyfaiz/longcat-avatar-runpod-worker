# LongCat Avatar 1.5 RunPod Worker

Minimal queue worker for `meituan-longcat/LongCat-Video-Avatar-1.5`.

The container expects a persistent volume at `/runpod-volume`, downloads only the INT8 avatar weights plus the base tokenizer/text encoder/VAE, and returns a Base64 MP4.

Recommended endpoint settings:

- GPU: A100/H100/H200 80GB, one GPU per worker
- Container disk: 30GB
- Network volume: 60GB mounted at `/runpod-volume`
- Workers: min 0, max 1
- Execution timeout: 3600 seconds
- Environment: `RUNPOD_INIT_TIMEOUT=3600`

Request body:

```json
{
  "input": {
    "image": "data:image/png;base64,...",
    "audio": "data:audio/wav;base64,...",
    "prompt": "A person faces the camera and speaks naturally.",
    "segments": 1,
    "resolution": "480p"
  }
}
```
