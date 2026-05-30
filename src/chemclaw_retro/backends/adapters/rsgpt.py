"""RSGPT — generative transformer pretrained on ~10B template-generated
reactions. Weights on Zenodo (10.5281/zenodo.15336192)."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="rsgpt",
    family="llm",
    license="MIT",
    citation="Liu et al., Nat. Commun. 2025",
    capabilities=["single_step"],
    url="https://github.com/jogjogee/RSGPT",
    deploy=BackendDeploy(
        dockerfile="docker/backends/hf_llm.Dockerfile",
        service="rsgpt",
        host_port=9050,
        profiles=["phase3", "llm"],
        gpu=True,
        environment={
            "BACKEND_NAME": "rsgpt",
            "BACKEND_CITATION": "Liu et al., Nat. Commun. 2025",
            "BACKEND_URL": "https://github.com/jogjogee/RSGPT",
            "BACKEND_LICENSE": "MIT",
            "HF_MODEL_PATH": "${RSGPT_CKPT:-/weights/rsgpt}",
            "LLM_MAX_NEW_TOKENS": "192",
        },
    ),
)
