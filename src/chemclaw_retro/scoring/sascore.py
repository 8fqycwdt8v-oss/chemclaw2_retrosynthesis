"""SAscore — Synthetic Accessibility score (RDKit contrib, BSD).

Implementation lives in RDKit's ``Contrib/SA_Score``. We try to import it
directly; if the contrib dir isn't on PYTHONPATH we return None so the
aggregator simply skips the feature.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def sa_score(smiles: str) -> float | None:
    try:
        import os
        import sys

        from rdkit import Chem
        from rdkit.Chem import RDConfig  # type: ignore[attr-defined]

        sys.path.append(os.path.join(RDConfig.RDContribDir, "SA_Score"))
        import sascorer  # type: ignore[import-not-found]
    except Exception as e:  # pragma: no cover — depends on RDKit build
        log.debug("SAscore unavailable: %s", e)
        return None
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return float(sascorer.calculateScore(mol))
