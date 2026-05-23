FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y git && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/duartegroup/Het-retro.git /opt/het \
 && pip install -r /opt/het/requirements.txt 2>/dev/null \
 && pip install fastapi "uvicorn[standard]" pydantic rdkit
ENV PYTHONPATH=/opt/het
COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/het_retro_service.py /app/service.py
EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
