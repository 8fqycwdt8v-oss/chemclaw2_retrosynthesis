"""rxnfp — reaction fingerprints + BERT-based classification (IBM RXN +
Reymond Group). MIT licensed."""

from __future__ import annotations

import asyncio
import logging

from .._lazy import TTLLoader

log = logging.getLogger(__name__)


def _make_pipe() -> object:
    from rxnfp.transformer_fingerprints import (  # type: ignore[import-not-found]
        RXNBERTFingerprintGenerator,
        get_default_model_and_tokenizer,
    )

    model, tokenizer = get_default_model_and_tokenizer()
    return RXNBERTFingerprintGenerator(model, tokenizer)


_LOADER: TTLLoader[object] = TTLLoader(_make_pipe, name="rxnfp")


async def classify_rxnfp(rxn_smiles: str) -> dict[str, float | str | None]:
    p = await asyncio.to_thread(_LOADER.get)
    if p is None:
        return {"class": None, "confidence": None}
    # rxnfp produces fingerprints; the downstream classifier head ships
    # in the rxnfp model card. Phase 1 emits a placeholder until the
    # rxnfp classification head is wired in by the rxnfp-side container.
    try:
        await asyncio.to_thread(p.convert, rxn_smiles)  # type: ignore[attr-defined]
        return {"class": "unknown", "confidence": None}
    except Exception as e:  # pragma: no cover
        log.debug("rxnfp inference failed: %s", e)
        return {"class": None, "confidence": None}
