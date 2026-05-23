FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y git && rm -rf /var/lib/apt/lists/*
# Upstream repo URL will be filled in once the authors publish their code.
RUN pip install fastapi "uvicorn[standard]" pydantic rdkit
COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/enzyformer_service.py /app/service.py
EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
