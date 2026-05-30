"""FusionRetro — in-context learning for retrosynthetic planning."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="fusionretro",
    family="transformer",
    license="MIT",
    citation="Liu et al., ICML 2023",
    capabilities=["single_step", "multi_step"],
    url="https://github.com/SongtaoLiu0823/FusionRetro",
    deploy=BackendDeploy(
        dockerfile="docker/backends/fusionretro.Dockerfile",
        service="fusionretro",
        host_port=9027,
        profiles=["phase2", "transformer"],
        gpu=True,
    ),
)
