# RetroSim — similarity-based single-step. Lightweight, no GPU needed.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y git build-essential \
                                                            libxrender1 libxext6 libsm6 libgl1 \
 && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/connorcoley/retrosim.git /opt/retrosim \
 && pip install -e /opt/retrosim 2>/dev/null \
 && pip install rdchiral fastapi "uvicorn[standard]" pydantic rdkit pandas

ENV PYTHONPATH=/opt/retrosim

COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/retrosim_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
