# GLN — Conditional Graph Logic Network (Dai et al., NeurIPS 2019).

FROM pytorch/pytorch:1.5.0-cuda10.1-cudnn7-runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y git build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/Hanjun-Dai/GLN.git /opt/gln \
 && cd /opt/gln && pip install -e . 2>/dev/null \
 && pip install fastapi "uvicorn[standard]" pydantic rdkit

ENV PYTHONPATH=/opt/gln

COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/gln_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
