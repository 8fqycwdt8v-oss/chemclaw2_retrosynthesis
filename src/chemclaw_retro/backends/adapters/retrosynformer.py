"""RetroSynFormer — Decision-Transformer multi-step planner (emmaryd, RSC
Digital Discovery 2026). Trained on PaRoutes."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="retrosynformer",
    family="planner",
    license="Apache-2.0",
    citation="Rydholm et al., RSC Digital Discovery 2026",
    capabilities=["multi_step"],
    url="https://github.com/emmaryd/retrosynformer",
)
