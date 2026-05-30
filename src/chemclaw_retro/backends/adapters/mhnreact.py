"""MHNreact — Modern Hopfield Network for template relevance (JKU Linz)."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="mhnreact",
    family="template",
    license="MIT",
    citation="Seidl et al., NeurIPS 2022 (AI4Science)",
    capabilities=["single_step"],
    url="https://github.com/ml-jku/mhn-react",
    deploy=BackendDeploy(
        dockerfile="docker/backends/mhnreact.Dockerfile",
        service="mhnreact",
        host_port=9011,
        profiles=["phase2", "template"],
        gpu=True,
    ),
)
