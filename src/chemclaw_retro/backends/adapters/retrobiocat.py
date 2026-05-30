"""RetroBioCat — computer-aided design tool for biocatalytic cascades."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="retrobiocat",
    family="biocatalysis",
    license="MIT",
    citation="Finnigan et al., Nat. Catal. 2021",
    capabilities=["multi_step"],
    url="https://github.com/wjafinnigan/RetroBioCat",
    deploy=BackendDeploy(
        dockerfile="docker/backends/retrobiocat.Dockerfile",
        service="retrobiocat",
        host_port=9061,
        profiles=["phase4", "biocatalysis"],
        gpu=False,
    ),
)
