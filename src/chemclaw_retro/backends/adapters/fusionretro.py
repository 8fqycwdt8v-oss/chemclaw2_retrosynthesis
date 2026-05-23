"""FusionRetro — in-context learning for retrosynthetic planning."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="fusionretro",
    family="transformer",
    license="MIT",
    citation="Liu et al., ICML 2023",
    capabilities=["single_step", "multi_step"],
    url="https://github.com/SongtaoLiu0823/FusionRetro",
)
