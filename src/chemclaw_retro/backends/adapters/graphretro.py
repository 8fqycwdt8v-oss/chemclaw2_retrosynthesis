"""GraphRetro — two-stage graph model for one-step retrosynthesis
(Somnath et al., NeurIPS 2021)."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="graphretro",
    family="graph",
    license="MIT",
    citation="Somnath et al., NeurIPS 2021",
    capabilities=["single_step"],
    url="https://github.com/vsomnath/graphretro",
    deploy=BackendDeploy(
        dockerfile="docker/backends/graphretro.Dockerfile",
        service="graphretro",
        host_port=9032,
        profiles=["phase2", "graph"],
        gpu=True,
    ),
)
