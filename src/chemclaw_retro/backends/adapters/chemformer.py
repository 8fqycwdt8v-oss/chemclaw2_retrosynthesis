"""Chemformer adapter — both retrosynthesis and forward (round-trip).

Same pattern as ``aizynth``: the heavy model runs in its own container,
the gateway talks to it via :class:`RemoteBackend`."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="chemformer",
    family="transformer",
    license="Apache-2.0",
    citation="Irwin et al., Mach. Learn.: Sci. Technol. 2022",
    capabilities=["single_step", "forward"],
    url="https://github.com/MolecularAI/Chemformer",
)
