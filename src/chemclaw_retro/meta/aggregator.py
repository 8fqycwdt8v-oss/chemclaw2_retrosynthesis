"""Take the per-backend predictions, group by canonical reactant set,
score with the chosen reranker, and return a sorted ``MetaPrediction``
list with full provenance.

Round-trip validation, RAscore lookup, and rxnfp classification are
injected as awaitable callables so that the gateway can wire in whatever
forward / scoring backends are healthy at the time.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from .._async_utils import safe_gather_map
from ..canonical import canonical_smiles, canonicalize_reactants
from ..schemas import (
    BackendContribution,
    MetaPrediction,
    SinglePrediction,
)
from .features import GroupFeatures, normalise_score, per_backend_minmax, reciprocal_rank_fusion
from .reranker import Reranker

log = logging.getLogger(__name__)

# Hooks the gateway plugs in:
ForwardChecker = Callable[[str, list[str]], Awaitable[bool]]
"""(target_canonical, reactant_canonicals) → True if forward model
reproduces target."""

RAScorer = Callable[[list[str]], Awaitable[float | None]]
SCScorer = Callable[[list[str]], Awaitable[float | None]]


@dataclass
class _Group:
    reactants: list[str]
    contributions: list[tuple[str, SinglePrediction]]


async def aggregate(
    target: str,
    per_backend: dict[str, list[SinglePrediction]],
    *,
    reranker: Reranker,
    top_k: int,
    forward_checker: ForwardChecker | None = None,
    rascorer: RAScorer | None = None,
    scscorer: SCScorer | None = None,
    rrf_k: int = 60,
) -> list[MetaPrediction]:
    """Canonicalise → group → score → rerank → top-K."""

    canonical_target = canonical_smiles(target)
    groups: dict[str, _Group] = {}

    # Per-request memo over canonicalize_reactants: many backends emit
    # the same reactant list, and we'd otherwise hit RDKit for each
    # backend-prediction pair. The shared module-level lru_cache helps
    # but is concurrently shared and can churn under load.
    canon_memo: dict[tuple[str, ...], list[str]] = {}

    # Group by canonical reactant set, dropping any prediction whose
    # reactants don't canonicalise. canon_reactants preserves the per-
    # reactant boundary (so ['[Na+].[Cl-]', 'CCO'] stays two entries,
    # not three after a naive split on '.') — the round-trip checker
    # and the response payload both rely on that grouping.
    for backend, preds in per_backend.items():
        for p in preds:
            memo_key = tuple(p.reactants)
            try:
                canon_reactants = canon_memo.get(memo_key) or canonicalize_reactants(p.reactants)
            except ValueError:
                log.debug("backend=%s invalid SMILES in prediction, skipping", backend)
                continue
            canon_memo[memo_key] = canon_reactants
            key = ".".join(canon_reactants)
            g = groups.setdefault(key, _Group(canon_reactants, []))
            g.contributions.append((backend, p))

    if not groups:
        return []

    # Per-backend min-max for score normalisation.
    scores_by_backend: dict[str, list[float]] = defaultdict(list)
    for g in groups.values():
        for b, p in g.contributions:
            scores_by_backend[b].append(p.score)
    mm = per_backend_minmax(dict(scores_by_backend))

    # Optional async features. The three scorers are independent of
    # each other; fan them out concurrently so the feature-extraction
    # phase scales as max(ra, sc, forward) instead of their sum.
    keys = list(groups.keys())
    reactant_args = [(groups[k].reactants,) for k in keys]
    rt_args = [(canonical_target, groups[k].reactants) for k in keys]

    rascore_vals, scscore_vals, rt_vals = await asyncio.gather(
        safe_gather_map(rascorer, keys, reactant_args, label="rascorer"),
        safe_gather_map(scscorer, keys, reactant_args, label="scscorer"),
        safe_gather_map(forward_checker, keys, rt_args, label="round_trip"),
    )

    results: list[MetaPrediction] = []
    for k, g in groups.items():
        rrf = reciprocal_rank_fusion(g.contributions, k=rrf_k)
        norm_scores = [normalise_score(b, p.score, mm) for b, p in g.contributions]
        mean_norm = sum(norm_scores) / len(norm_scores) if norm_scores else 0.0

        rascore_min = rascore_vals.get(k)
        scscore_max = scscore_vals.get(k)
        round_trip = rt_vals.get(k)

        feats = GroupFeatures(
            consensus_count=len({b for b, _ in g.contributions}),
            rrf_score=rrf,
            mean_norm_score=mean_norm,
            rascore_min=rascore_min,
            scscore_max=scscore_max,
            round_trip_ok=round_trip,
            rxnfp_class_match=None,
        )
        final = reranker.score(feats)

        provenance = sorted(
            (
                BackendContribution(
                    backend=b,
                    rank=p.rank,
                    score=p.score,
                    template_id=p.template_id,
                )
                for b, p in g.contributions
            ),
            key=lambda c: c.score,
            reverse=True,
        )

        results.append(
            MetaPrediction(
                reactants=g.reactants,
                final_score=final,
                consensus_count=feats.consensus_count,
                features=feats.as_dict(),
                round_trip_ok=round_trip,
                provenance=provenance,
            )
        )

    results.sort(key=lambda r: r.final_score, reverse=True)
    return results[:top_k]
