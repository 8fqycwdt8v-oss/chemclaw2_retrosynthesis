"""R-SMILES — root-aligned SMILES transformer (otori-bird)."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="rsmiles",
    family="transformer",
    license="MIT",
    citation="Zhong et al., Chem. Sci. 2022",
    capabilities=["single_step"],
    url="https://github.com/otori-bird/retrosynthesis",
)
