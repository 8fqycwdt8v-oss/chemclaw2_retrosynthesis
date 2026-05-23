# DeepRetro — recursive-LLM hybrid (Deep Forest Sciences).
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y git libxrender1 libxext6 libsm6 libgl1 \
 && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/deepforestsci/DeepRetro.git /opt/dr \
 && pip install -e /opt/dr 2>/dev/null \
 && pip install fastapi "uvicorn[standard]" pydantic rdkit anthropic
ENV PYTHONPATH=/opt/dr
COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/deepretro_service.py /app/service.py
EXPOSE 9000
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
