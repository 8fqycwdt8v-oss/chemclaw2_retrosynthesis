"""ChemDFM-13B — chemistry foundation LLM (HuggingFace)."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="chemdfm",
    family="llm",
    license="Apache-2.0",
    citation="Zhao et al., arXiv:2401.14818",
    capabilities=["single_step"],
    url="https://huggingface.co/OpenDFM/ChemDFM-13B-v1.0",
    deploy=BackendDeploy(
        dockerfile="docker/backends/hf_llm.Dockerfile",
        service="chemdfm",
        host_port=9051,
        profiles=["phase3", "llm"],
        gpu=True,
        environment={
            "BACKEND_NAME": "chemdfm",
            "BACKEND_CITATION": "Zhao et al., arXiv:2401.14818",
            "BACKEND_URL": "https://huggingface.co/OpenDFM/ChemDFM-13B-v1.0",
            "HF_MODEL_ID": "${CHEMDFM_HF_MODEL_ID:-OpenDFM/ChemDFM-13B-v1.0}",
        },
    ),
)
