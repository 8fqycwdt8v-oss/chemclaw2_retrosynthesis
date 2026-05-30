"""LocalRetro — atom/bond-local template-based retrosynthesis (KAIST).

Apache 2.0; pretrained weights for USPTO-50K (658 local templates) and
USPTO-MIT (20,221 templates) are bundled with the upstream repo. The
heavy model runs in its own Docker image and is exposed to the gateway
via :class:`RemoteBackend`.
"""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="localretro",
    family="template",
    license="Apache-2.0",
    citation="Chen & Jung, JACS Au 2021",
    capabilities=["single_step"],
    url="https://github.com/kaist-amsg/LocalRetro",
    deploy=BackendDeploy(
        dockerfile="docker/backends/localretro.Dockerfile",
        service="localretro",
        host_port=9010,
        profiles=["phase2", "template"],
        gpu=True,
    ),
)
