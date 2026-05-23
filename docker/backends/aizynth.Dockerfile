# AiZynthFinder backend microservice. Heavy deps (TensorFlow/ONNX, RDKit
# pinned to the version aizynth requires) so it lives in its own image.
#
# The image expects pretrained policy + ZINC stock under /weights; mount
# the host directory populated by scripts/download_weights.sh aizynth.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    AIZYNTH_CONFIG=/weights/aizynth/config.yml

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y libxrender1 libxext6 libsm6 libgl1 git curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
 && pip install "aizynthfinder>=4.4" "fastapi>=0.115" "uvicorn[standard]>=0.30" "pydantic>=2.8"

# The microservice wraps AiZynthFinder's Python API as the uniform
# /predict + /plan + /info + /healthz contract the gateway expects.
COPY docker/backends/aizynth_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]

CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
