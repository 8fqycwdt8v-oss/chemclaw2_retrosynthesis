"""DeepRetro — recursive-LLM + traditional-engine hybrid with
human-in-the-loop UI (Deep Forest Sciences)."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="deepretro",
    family="hybrid",
    license="MIT",
    citation="Deep Forest Sciences, arXiv:2507.07060",
    capabilities=["multi_step"],
    url="https://github.com/deepforestsci/DeepRetro",
)
