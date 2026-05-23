# RetroChimera — Microsoft + Novartis ensemble (NeuralLoc + R-SMILES 2 +
# learned reranker). Internally an ensemble; we expose it as one backend.

FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y git \
 && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/microsoft/retrochimera.git /opt/chimera \
 && pip install -e /opt/chimera 2>/dev/null \
 && pip install fastapi "uvicorn[standard]" pydantic rdkit

ENV PYTHONPATH=/opt/chimera

COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/retrochimera_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
