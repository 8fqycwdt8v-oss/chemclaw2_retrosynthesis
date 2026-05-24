"""rxnfp — reaction fingerprints + BERT-based classification (IBM RXN +
Reymond Group). MIT licensed.

Lazy import; if rxnfp isn't installed the route returns empty results
rather than 500-ing. Loader retries after a TTL so a late dep install
recovers without a process restart.
"""

from __future__ import annotations

import asyncio
import logging
import time

log = logging.getLogger(__name__)

_RETRY_INTERVAL_S = 60.0

_pipe: object | None = None
_last_failure_at: float = 0.0


def _load() -> object | None:
    global _pipe, _last_failure_at
    if _pipe is not None:
        return _pipe
    now = time.monotonic()
    if now - _last_failure_at < _RETRY_INTERVAL_S:
        return None
    try:
        from rxnfp.transformer_fingerprints import (  # type: ignore[import-not-found]
            RXNBERTFingerprintGenerator,
            get_default_model_and_tokenizer,
        )

        model, tokenizer = get_default_model_and_tokenizer()
        _pipe = RXNBERTFingerprintGenerator(model, tokenizer)
        return _pipe
    except Exception as e:  # pragma: no cover — optional dep
        log.debug("rxnfp unavailable (will retry after %.0fs): %s", _RETRY_INTERVAL_S, e)
        _last_failure_at = now
        return None


async def classify_rxnfp(rxn_smiles: str) -> dict[str, float | str | None]:
    p = await asyncio.to_thread(_load)
    if p is None:
        return {"class": None, "confidence": None}
    # rxnfp produces fingerprints; downstream classifier is bundled in the
    # rxnfp model card. For Phase 1 we just emit a placeholder until the
    # rxnfp classification head is wired in by the rxnfp-side container.
    try:
        await asyncio.to_thread(p.convert, rxn_smiles)  # type: ignore[attr-defined]
        return {"class": "unknown", "confidence": None}
    except Exception as e:  # pragma: no cover
        log.debug("rxnfp inference failed: %s", e)
        return {"class": None, "confidence": None}
