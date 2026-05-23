"""SMILES canonicalisation and grouping helpers — the linchpin of the
meta-aggregator.

We import RDKit lazily so the module imports cleanly in environments where
RDKit isn't installed (e.g. doc generation, light CI jobs). At call time
RDKit must be available — failing closed is intentional.
"""

from __future__ import annotations

from collections.abc import Iterable
from functools import lru_cache


@lru_cache(maxsize=4096)
def canonical_smiles(smiles: str, *, keep_stereo: bool = True) -> str:
    """Return RDKit-canonical SMILES; raise ValueError on invalid input."""
    from rdkit import Chem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"invalid SMILES: {smiles!r}")
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=keep_stereo)


def canonicalize_reactants(reactants: Iterable[str], *, keep_stereo: bool = True) -> list[str]:
    """Canonicalise each reactant SMILES and return them sorted, so that the
    list is a stable group key irrespective of input order or atom mapping."""
    canon = [canonical_smiles(r, keep_stereo=keep_stereo) for r in reactants if r]
    canon.sort()
    return canon


def group_key(reactants: Iterable[str], *, keep_stereo: bool = True) -> str:
    """Stable hashable key for a reactant set."""
    return ".".join(canonicalize_reactants(reactants, keep_stereo=keep_stereo))


def strip_atom_maps(smiles: str) -> str:
    """Drop atom-map numbers from a SMILES string."""
    from rdkit import Chem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return smiles
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol, canonical=True)
