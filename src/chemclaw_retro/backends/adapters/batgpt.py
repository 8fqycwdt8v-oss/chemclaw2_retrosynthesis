"""BatGPT-Chem — 15B-param chemistry foundation LLM."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="batgpt",
    family="llm",
    license="Apache-2.0",
    citation="Liu et al., arXiv:2408.10285",
    capabilities=["single_step"],
    url="https://arxiv.org/abs/2408.10285",
    deploy=BackendDeploy(
        dockerfile="docker/backends/hf_llm.Dockerfile",
        service="batgpt",
        host_port=9052,
        profiles=["phase3", "llm"],
        gpu=True,
        environment={
            "BACKEND_NAME": "batgpt",
            "BACKEND_CITATION": "Liu et al., arXiv:2408.10285",
            "BACKEND_URL": "https://arxiv.org/abs/2408.10285",
            "HF_MODEL_ID": "${BATGPT_HF_MODEL_ID:?BATGPT_HF_MODEL_ID must be set in the host env}",
        },
    ),
)
