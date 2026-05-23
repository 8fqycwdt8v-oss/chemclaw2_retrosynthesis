# MHNreact (JKU Linz) — Modern Hopfield Network template scoring.

FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y git \
 && rm -rf /var/lib/apt/lists/*

RUN pip install mhnreact fastapi "uvicorn[standard]" pydantic rdkit

COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/mhnreact_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
