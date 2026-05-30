"""Het-retro — heterocycle-specialised single-step retrosynthesis
(Duarte group)."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="het_retro",
    family="transformer",
    license="MIT",
    citation="Duarte group, 2025",
    capabilities=["single_step"],
    url="https://github.com/duartegroup/Het-retro",
    deploy=BackendDeploy(
        dockerfile="docker/backends/het_retro.Dockerfile",
        service="het-retro",
        host_port=9028,
        profiles=["phase2", "transformer"],
        gpu=True,
    ),
)
