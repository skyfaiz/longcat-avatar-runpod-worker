FROM pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    LONGCAT_REPO=/opt/longcat \
    LONGCAT_MODEL_ROOT=/runpod-volume/models

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg gcc git libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt
RUN git clone --depth 1 https://github.com/meituan-longcat/LongCat-Video.git longcat && \
    sed -i -e '/^libsndfile1==/d' -e '/^tritonserverclient==/d' /opt/longcat/requirements_avatar.txt && \
    pip install packaging psutil ninja && \
    pip install "https://github.com/Dao-AILab/flash-attention/releases/download/v2.7.4.post1/flash_attn-2.7.4.post1%2Bcu12torch2.6cxx11abiFALSE-cp311-cp311-linux_x86_64.whl" && \
    pip install -r /opt/longcat/requirements.txt -r /opt/longcat/requirements_avatar.txt runpod "huggingface_hub[hf_transfer]"

WORKDIR /opt/worker
COPY handler.py sync_models.py entrypoint.sh ./
CMD ["bash", "/opt/worker/entrypoint.sh"]
