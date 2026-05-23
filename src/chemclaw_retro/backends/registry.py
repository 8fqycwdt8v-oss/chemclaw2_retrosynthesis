"""Discovers which backends are enabled and constructs adapters lazily.

The gateway never imports heavy ML deps directly; adapters either talk to
remote containers (:class:`RemoteBackend`) or, for backends shipped as
ordinary Python packages (e.g. AiZynthFinder), wrap their public API in
their own subprocess/process pool.
"""

from __future__ import annotations

from collections.abc import Iterable
from functools import lru_cache

from ..config import BackendEndpoint, Settings, get_settings
from .base import SingleStepBackend
from .remote import RemoteBackend


def _enabled_endpoints(settings: Settings) -> dict[str, BackendEndpoint]:
    out: dict[str, BackendEndpoint] = {}
    for field_name in settings.model_fields:
        if not field_name.startswith("backend_"):
            continue
        endpoint: BackendEndpoint = getattr(settings, field_name)
        if endpoint.enabled:
            out[field_name.removeprefix("backend_")] = endpoint
    return out


@lru_cache(maxsize=1)
def all_backends() -> dict[str, SingleStepBackend]:
    """Return ``{name: backend}`` for every enabled single-step backend.

    Cached for the lifetime of the process; restart the gateway to pick up
    config changes.
    """
    settings = get_settings()
    return {
        name: RemoteBackend(name, ep.url, timeout_s=ep.timeout_s)
        for name, ep in _enabled_endpoints(settings).items()
    }


def select_backends(names: Iterable[str] | str) -> list[SingleStepBackend]:
    """Resolve a request's ``backends`` field to concrete adapter instances."""
    available = all_backends()
    if names == "auto":
        return list(available.values())
    missing = [n for n in names if n not in available]
    if missing:
        raise ValueError(f"unknown or disabled backends: {missing}")
    return [available[n] for n in names]


def reset_registry_cache() -> None:
    """Test helper — clear the lru_cache on ``all_backends`` if present.

    Safe to call after monkeypatching ``all_backends`` to a non-cached
    function, in which case it is a no-op.
    """
    cache_clear = getattr(all_backends, "cache_clear", None)
    if cache_clear is not None:
        cache_clear()
