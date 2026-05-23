# ASKCOS — MIT's open-source synthesis-planning suite.
# Heavy image (~10GB) because it bundles four single-step models + MCTS
# planner + condition models. Prefer the upstream's official Compose
# file in production; this is a self-contained thin wrapper.

FROM askcos/askcos:latest  # upstream's published image (MIT-licensed)

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

RUN pip install fastapi "uvicorn[standard]" pydantic

COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/askcos_service.py /app/service.py

WORKDIR /app
EXPOSE 9000
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
