# MEGAN (Molecule.one) — graph-edit attention network.
# Weights ship as megan_data.zip on the v1.1 GitHub release; mount at
# /weights/megan/.

FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y git build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/molecule-one/megan.git /opt/megan \
 && pip install -r /opt/megan/requirements.txt 2>/dev/null \
 && pip install "fastapi" "uvicorn[standard]" pydantic

ENV PYTHONPATH=/opt/megan

COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/megan_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]

CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
