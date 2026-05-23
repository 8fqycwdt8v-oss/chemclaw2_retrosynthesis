# Graph2SMILES (Coley group) — permutation-invariant graph→seq.

FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y git \
 && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/coleygroup/Graph2SMILES.git /opt/g2s \
 && pip install -r /opt/g2s/requirements.txt 2>/dev/null \
 && pip install fastapi "uvicorn[standard]" pydantic rdkit

ENV PYTHONPATH=/opt/g2s

COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/graph2smiles_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
