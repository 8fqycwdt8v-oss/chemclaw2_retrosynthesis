"""DeepRetro — recursive-LLM + traditional-engine hybrid with
human-in-the-loop UI (Deep Forest Sciences)."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="deepretro",
    family="hybrid",
    license="MIT",
    citation="Deep Forest Sciences, arXiv:2507.07060",
    capabilities=["multi_step"],
    url="https://github.com/deepforestsci/DeepRetro",
    deploy=BackendDeploy(
        dockerfile="docker/backends/deepretro.Dockerfile",
        service="deepretro",
        host_port=9054,
        profiles=["phase3", "llm"],
        gpu=False,
        environment={"ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY:-}"},
    ),
)
