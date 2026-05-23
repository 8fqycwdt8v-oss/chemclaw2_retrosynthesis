"""READRetro — natural-product biosynthesis with retrieval-augmented
dual-view retrosynthesis."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="readretro",
    family="biocatalysis",
    license="MIT",
    citation="Lee et al., New Phytol. 2024",
    capabilities=["multi_step"],
    url="https://github.com/SeulLee05/READRetro",
)
