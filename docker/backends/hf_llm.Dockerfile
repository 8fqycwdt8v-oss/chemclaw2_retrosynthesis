# Generic HuggingFace-LLM backend image. One image hosts ChemDFM,
# BatGPT-Chem, RetroDFM-R, RSGPT, and any future chemistry LLM —
# pass HF_MODEL_ID or HF_MODEL_PATH + BACKEND_* env per service.

FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

RUN pip install transformers accelerate sentencepiece \
                "fastapi" "uvicorn[standard]" pydantic rdkit

WORKDIR /app
COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/hf_llm_service.py /app/service.py

EXPOSE 9000
VOLUME ["/weights"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
