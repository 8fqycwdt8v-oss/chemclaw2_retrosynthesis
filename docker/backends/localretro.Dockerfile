# LocalRetro (KAIST) — template-based local-attention model.

FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
 && apt-get install --no-install-recommends -y git \
 && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/kaist-amsg/LocalRetro.git /opt/localretro \
 && pip install dgl==1.1.0 dgllife==0.3.2 "fastapi" "uvicorn[standard]" pydantic rdkit \
 && pip install -e /opt/localretro 2>/dev/null || true

ENV PYTHONPATH=/opt/localretro

COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/localretro_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]

CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
