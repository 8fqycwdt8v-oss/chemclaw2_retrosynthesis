"""Tied Two-Way Transformer — bi-directional transformer for valid,
plausible, diverse retrosynthesis."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="tied_twoway",
    family="transformer",
    license="MIT",
    citation="Lee et al., JCIM 2022",
    capabilities=["single_step"],
    url="https://github.com/ejklike/tied-twoway-transformer",
    deploy=BackendDeploy(
        dockerfile="docker/backends/tied_twoway.Dockerfile",
        service="tied-twoway",
        host_port=9026,
        profiles=["phase2", "transformer"],
        gpu=True,
    ),
)
