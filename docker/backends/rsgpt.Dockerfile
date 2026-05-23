# RSGPT — generative transformer pretrained on ~10B template-generated
# reactions. Weights from Zenodo.

FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y git wget \
 && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/jogjogee/RSGPT.git /opt/rsgpt 2>/dev/null || true \
 && pip install transformers fastapi "uvicorn[standard]" pydantic rdkit

ENV PYTHONPATH=/opt/rsgpt
COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/rsgpt_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
