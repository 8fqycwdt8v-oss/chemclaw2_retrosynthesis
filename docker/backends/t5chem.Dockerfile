FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN pip install t5chem fastapi "uvicorn[standard]" pydantic rdkit
COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/t5chem_service.py /app/service.py
EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
