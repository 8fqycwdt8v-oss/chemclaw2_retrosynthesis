FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y git && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/reymond-group/MultiStepRetrosynthesisTTL.git /opt/ttl \
 && pip install -e /opt/ttl 2>/dev/null \
 && pip install fastapi "uvicorn[standard]" pydantic rdkit
ENV PYTHONPATH=/opt/ttl
COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/ttl_service.py /app/service.py
EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
