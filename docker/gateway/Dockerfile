FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Build deps for RDKit wheels on slim images.
RUN apt-get update \
    && apt-get install --no-install-recommends -y libxrender1 libxext6 libsm6 libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN pip install --upgrade pip \
 && pip install ".[scoring]"

EXPOSE 8000

CMD ["uvicorn", "chemclaw_retro.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
