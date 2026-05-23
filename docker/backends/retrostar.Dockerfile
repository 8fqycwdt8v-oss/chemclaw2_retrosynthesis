# Retro* — neural-guided A* search.

FROM pytorch/pytorch:1.7.0-cuda11.0-cudnn8-runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y git \
 && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/binghong-ml/retro_star.git /opt/retro_star \
 && pip install -e /opt/retro_star 2>/dev/null \
 && pip install fastapi "uvicorn[standard]" pydantic rdkit

ENV PYTHONPATH=/opt/retro_star

COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/retrostar_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
