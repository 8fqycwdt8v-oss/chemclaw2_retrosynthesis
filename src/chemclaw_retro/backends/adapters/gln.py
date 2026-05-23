"""GLN — Conditional Graph Logic Network for retrosynthesis (Dai et al.,
NeurIPS 2019). Checkpoints on Dropbox; see scripts/download_weights.sh."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="gln",
    family="graph",
    license="MIT",
    citation="Dai et al., NeurIPS 2019",
    capabilities=["single_step"],
    url="https://github.com/Hanjun-Dai/GLN",
)
