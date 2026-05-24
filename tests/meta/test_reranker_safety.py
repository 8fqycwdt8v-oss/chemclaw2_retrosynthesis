"""Regression: HeuristicReranker.from_yaml must fail loudly with a
useful message when the weights file is missing or malformed, and the
single_step _reranker() must refuse to silently fall back when the
operator asked for the learned reranker but forgot to set the model
path."""

from __future__ import annotations

from pathlib import Path

import pytest

from chemclaw_retro.meta.reranker import HeuristicReranker


def test_missing_weights_file_raises_clear_error(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="not found"):
        HeuristicReranker.from_yaml(tmp_path / "nonexistent.yaml")


def test_empty_weights_file_is_treated_as_empty_dict(tmp_path: Path) -> None:
    p = tmp_path / "empty.yaml"
    p.write_text("# only comments\n")
    rr = HeuristicReranker.from_yaml(p)
    assert rr.w == {}


def test_non_mapping_weights_file_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("- just\n- a\n- list\n")
    with pytest.raises(RuntimeError, match="mapping"):
        HeuristicReranker.from_yaml(p)


def test_learned_reranker_misconfig_fails_loudly(monkeypatch: pytest.MonkeyPatch) -> None:
    import chemclaw_retro.config as cfg
    from chemclaw_retro.server.routes import single_step as ss

    monkeypatch.setenv("CHEMCLAW_RETRO_RERANKER", "learned")
    monkeypatch.delenv("CHEMCLAW_RETRO_LEARNED_MODEL", raising=False)
    monkeypatch.setattr(cfg, "_settings", None)
    ss.reset_reranker_cache()
    try:
        with pytest.raises(RuntimeError, match="LEARNED_MODEL"):
            ss._reranker()
    finally:
        monkeypatch.setattr(cfg, "_settings", None)
        ss.reset_reranker_cache()
