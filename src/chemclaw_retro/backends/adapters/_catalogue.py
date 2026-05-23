"""Central catalogue of every adapter's ``BackendInfo`` so the
``/backends`` endpoint can surface license / family / citation metadata
even when the remote container is unhealthy.
"""

from __future__ import annotations

from ...schemas import BackendInfo
from . import (
    aizynth,
    askcos,
    batgpt,
    chemdfm,
    chemformer,
    deepretro,
    desp,
    directmultistep,
    disconnection_chemformer,
    enzyformer,
    fusionretro,
    g2retro,
    gln,
    graph2smiles,
    graphretro,
    het_retro,
    localretro,
    megan,
    mhnreact,
    neuralsym,
    openretro,
    readretro,
    retrobiocat,
    retrobridge,
    retrochimera,
    retrocomposer,
    retrodfm,
    retroformer,
    retropath,
    retroprime,
    retrosim,
    retrostar,
    retrosynformer,
    retroxpert,
    rsgpt,
    rsmiles,
    synplanner,
    syntheseus,
    t5chem,
    tied_twoway,
    ttl,
)

CATALOGUE: dict[str, BackendInfo] = {
    info.name: info
    for info in (
        aizynth.INFO,
        askcos.INFO,
        batgpt.INFO,
        chemdfm.INFO,
        chemformer.INFO,
        deepretro.INFO,
        desp.INFO,
        directmultistep.INFO,
        disconnection_chemformer.INFO,
        enzyformer.INFO,
        fusionretro.INFO,
        g2retro.INFO,
        gln.INFO,
        graph2smiles.INFO,
        graphretro.INFO,
        het_retro.INFO,
        localretro.INFO,
        megan.INFO,
        mhnreact.INFO,
        neuralsym.INFO,
        openretro.INFO,
        readretro.INFO,
        retrobiocat.INFO,
        retrobridge.INFO,
        retrochimera.INFO,
        retrocomposer.INFO,
        retrodfm.INFO,
        retroformer.INFO,
        retropath.INFO,
        retroprime.INFO,
        retrosim.INFO,
        retrostar.INFO,
        retrosynformer.INFO,
        retroxpert.INFO,
        rsgpt.INFO,
        rsmiles.INFO,
        synplanner.INFO,
        syntheseus.INFO,
        t5chem.INFO,
        tied_twoway.INFO,
        ttl.INFO,
    )
}


def get_info(name: str) -> BackendInfo | None:
    return CATALOGUE.get(name)


def all_known_backends() -> list[BackendInfo]:
    return list(CATALOGUE.values())
