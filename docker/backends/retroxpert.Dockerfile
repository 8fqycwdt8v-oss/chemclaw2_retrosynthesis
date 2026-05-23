FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y git && rm -rf /var/lib/apt/lists/*
# Use the leak-fix branch only (per upstream disclosure).
RUN git clone --depth 1 -b leak_fix https://github.com/uta-smile/RetroXpert.git /opt/rx 2>/dev/null \
 || git clone --depth 1 https://github.com/uta-smile/RetroXpert.git /opt/rx \
 && pip install -r /opt/rx/requirements.txt 2>/dev/null \
 && pip install fastapi "uvicorn[standard]" pydantic rdkit
ENV PYTHONPATH=/opt/rx
COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/retroxpert_service.py /app/service.py
EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
