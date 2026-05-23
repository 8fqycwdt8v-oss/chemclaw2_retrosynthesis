"""Retroformer — end-to-end retrosynthesis transformer (Wan et al., ICML 2022)."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="retroformer",
    family="transformer",
    license="MIT",
    citation="Wan et al., ICML 2022",
    capabilities=["single_step"],
    url="https://github.com/yuewan2/Retroformer",
)
