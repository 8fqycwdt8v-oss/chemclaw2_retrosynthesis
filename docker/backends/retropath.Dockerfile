FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y git libxrender1 libxext6 libsm6 libgl1 \
 && rm -rf /var/lib/apt/lists/*
RUN pip install retropath_rl fastapi "uvicorn[standard]" pydantic rdkit
COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/retropath_service.py /app/service.py
EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
