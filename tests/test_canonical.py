import pytest

from chemclaw_retro.canonical import (
    canonical_smiles,
    canonicalize_reactants,
    group_key,
    strip_atom_maps,
)


def test_canonicalises_equivalent_smiles():
    pytest.importorskip("rdkit")
    assert canonical_smiles("OCC") == canonical_smiles("CCO")


def test_reactant_group_key_is_order_independent():
    pytest.importorskip("rdkit")
    a = group_key(["CCO", "CC(=O)Cl"])
    b = group_key(["CC(=O)Cl", "CCO"])
    assert a == b


def test_canonicalize_drops_falsy_entries():
    pytest.importorskip("rdkit")
    out = canonicalize_reactants(["CCO", "", "CC(=O)Cl"])
    assert len(out) == 2


def test_strip_atom_maps():
    pytest.importorskip("rdkit")
    stripped = strip_atom_maps("[C:1][C:2]([H])([H])O")
    assert ":" not in stripped


def test_canonical_invalid_raises():
    pytest.importorskip("rdkit")
    with pytest.raises(ValueError):
        canonical_smiles("not a smiles")
