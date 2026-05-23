# RetroDFM-R — reasoning LLM for retrosynthesis.
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
ENV HF_MODEL_ID=OpenDFM/RetroDFM-R
RUN pip install transformers accelerate sentencepiece "fastapi" "uvicorn[standard]" pydantic rdkit
WORKDIR /app
COPY docker/backends/_base.py /app/_base.py
COPY docker/backends/_hf_llm_service.py /app/_hf_llm_service.py
COPY docker/backends/retrodfm_service.py /app/service.py
EXPOSE 9000
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9000"]
