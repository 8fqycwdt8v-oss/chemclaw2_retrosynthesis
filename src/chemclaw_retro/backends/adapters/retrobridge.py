"""RetroBridge — Markov bridge model for template-free retrosynthesis
(Igashov et al., ICLR 2024)."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="retrobridge",
    family="graph",
    license="MIT",
    citation="Igashov et al., ICLR 2024",
    capabilities=["single_step"],
    url="https://github.com/igashov/RetroBridge",
    deploy=BackendDeploy(
        dockerfile="docker/backends/retrobridge.Dockerfile",
        service="retrobridge",
        host_port=9033,
        profiles=["phase2", "graph"],
        gpu=True,
    ),
)
