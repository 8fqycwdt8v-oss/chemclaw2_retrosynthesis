FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y git && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/coleygroup/openretro.git /opt/openretro \
 && pip install -r /opt/openretro/requirements.txt 2>/dev/null \
 && pip install fastapi "uvicorn[standard]" pydantic rdkit
ENV PYTHONPATH=/opt/openretro
COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/openretro_service.py /app/service.py
EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
