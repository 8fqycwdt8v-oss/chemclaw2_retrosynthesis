"""RetroDFM-R — reasoning LLM for retrosynthesis (currently SoTA on
USPTO-50K with 65% top-1 as of mid-2025)."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="retrodfm",
    family="llm",
    license="Apache-2.0",
    citation="arXiv:2507.17448",
    capabilities=["single_step"],
    url="https://arxiv.org/abs/2507.17448",
    deploy=BackendDeploy(
        dockerfile="docker/backends/hf_llm.Dockerfile",
        service="retrodfm",
        host_port=9053,
        profiles=["phase3", "llm"],
        gpu=True,
        environment={
            "BACKEND_NAME": "retrodfm",
            "BACKEND_CITATION": "arXiv:2507.17448",
            "BACKEND_URL": "https://arxiv.org/abs/2507.17448",
            "HF_MODEL_ID": "${RETRODFM_HF_MODEL_ID:-OpenDFM/RetroDFM-R}",
        },
    ),
)
