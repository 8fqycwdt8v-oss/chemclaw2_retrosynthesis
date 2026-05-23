"""RetroPath RL — bio-retrosynthesis via MCTS."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="retropath",
    family="biocatalysis",
    license="MIT",
    citation="Koch et al., bioRxiv 2019",
    capabilities=["multi_step"],
    url="https://github.com/brsynth/RetroPathRL",
)
