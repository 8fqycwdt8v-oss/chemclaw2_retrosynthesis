"""GraphRetro — two-stage graph model for one-step retrosynthesis
(Somnath et al., NeurIPS 2021)."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="graphretro",
    family="graph",
    license="MIT",
    citation="Somnath et al., NeurIPS 2021",
    capabilities=["single_step"],
    url="https://github.com/vsomnath/graphretro",
)
