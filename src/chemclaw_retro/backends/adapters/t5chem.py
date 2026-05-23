"""T5Chem — T5-based multitask model (forward / retro / yield / class).

Same model serves multiple capabilities; we register it under both
single-step retro and forward."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="t5chem",
    family="transformer",
    license="MIT",
    citation="Lu & Zhang, JCIM 2022",
    capabilities=["single_step", "forward", "classify"],
    url="https://github.com/HelloJocelynLu/t5chem",
)
