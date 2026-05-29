"""Shared test fixtures.

Many gateway tests need to swap in a controlled set of fake backends.
The :func:`registry_with` fixture (and its underlying
:func:`make_fake_backend` factory) consolidate the
``monkeypatch.setattr(registry, "all_backends", ...)`` + ``reset_registry_cache()``
incantation that was repeated in test_app, test_multi_step, and
test_select_backends.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest

import chemclaw_retro.backends.registry as registry
from chemclaw_retro.backends.base import SingleStepBackend
from chemclaw_retro.schemas import BackendInfo, SinglePrediction


class FakeSingleStepBackend(SingleStepBackend):
    """Minimal SingleStepBackend that returns canned predictions and
    is always healthy. Suitable for any test that exercises the gateway
    aggregation path without standing up a real backend container.
    """

    def __init__(
        self,
        name: str,
        preds: list[SinglePrediction] | None = None,
        *,
        family: str = "template",
    ) -> None:
        self.name = name
        self._preds = preds or []
        self._family = family

    async def info(self) -> BackendInfo:
        return BackendInfo(
            name=self.name, family=self._family, license="MIT", capabilities=["single_step"]
        )

    async def healthz(self) -> bool:
        return True

    async def predict(self, smiles: str, top_k: int = 25) -> list[SinglePrediction]:
        return self._preds[:top_k]


@pytest.fixture()
def make_fake_backend() -> Callable[..., FakeSingleStepBackend]:
    """Factory fixture: ``b = make_fake_backend("a", [SinglePrediction(...)])``."""

    def _make(
        name: str,
        preds: list[SinglePrediction] | None = None,
        *,
        family: str = "template",
    ) -> FakeSingleStepBackend:
        return FakeSingleStepBackend(name, preds, family=family)

    return _make


@pytest.fixture()
def registry_with(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Callable[[dict[str, SingleStepBackend]], None]]:
    """Install ``backends`` as the registry's live set. Handles the
    ``monkeypatch.setattr`` + ``reset_registry_cache`` dance and clears
    the cache again on teardown.
    """

    def _install(backends: dict[str, SingleStepBackend]) -> None:
        monkeypatch.setattr(registry, "all_backends", lambda: backends)
        registry.reset_registry_cache()

    yield _install
    registry.reset_registry_cache()
