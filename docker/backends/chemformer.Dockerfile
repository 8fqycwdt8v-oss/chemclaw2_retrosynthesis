# Chemformer (MolecularAI) — BART transformer for retrosynthesis + forward.
# Weights: download combined.ckpt from the upstream repo's instructions,
# mount at /weights/chemformer/combined.ckpt.

FROM nvcr.io/nvidia/pytorch:24.05-py3

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
 && apt-get install --no-install-recommends -y git \
 && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/MolecularAI/Chemformer.git /opt/chemformer \
 && pip install -e /opt/chemformer \
 && pip install fastapi "uvicorn[standard]" pydantic rdkit

COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/chemformer_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]

CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
