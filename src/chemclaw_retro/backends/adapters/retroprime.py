"""RetroPrime — diverse plausible transformer for single-step
retrosynthesis (Wang et al., Chem. Eng. J. 2021)."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="retroprime",
    family="transformer",
    license="MIT",
    citation="Wang et al., Chem. Eng. J. 2021",
    capabilities=["single_step"],
    url="https://github.com/wangxr0526/RetroPrime",
    deploy=BackendDeploy(
        dockerfile="docker/backends/retroprime.Dockerfile",
        service="retroprime",
        host_port=9022,
        profiles=["phase2", "transformer"],
        gpu=True,
    ),
)
