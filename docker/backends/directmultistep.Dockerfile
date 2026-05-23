# DirectMultiStep (Batista group) — multi-step routes via a single
# transformer decode. PyPI package.

FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install directmultistep fastapi "uvicorn[standard]" pydantic rdkit

COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/directmultistep_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
