"""DirectMultiStep — direct multi-step route generation as a single
transformer decode (Batista group, MIT)."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="directmultistep",
    family="planner",
    license="MIT",
    citation="Shee et al., JCIM 2025",
    capabilities=["multi_step"],
    url="https://github.com/batistagroup/DirectMultiStep",
)
