"""RetroComposer — composes templates for template-based retrosynthesis."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="retrocomposer",
    family="template",
    license="MIT",
    citation="Yan et al., Biomolecules 2022",
    capabilities=["single_step"],
    url="https://github.com/uta-smile/RetroComposer",
    deploy=BackendDeploy(
        dockerfile="docker/backends/retrocomposer.Dockerfile",
        service="retrocomposer",
        host_port=9013,
        profiles=["phase2", "template"],
        gpu=True,
    ),
)
