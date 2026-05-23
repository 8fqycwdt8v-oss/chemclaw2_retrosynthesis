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

from ..canonical import canonical_smiles, group_key
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

    # Group by canonical reactant set, dropping any prediction whose
    # reactants don't canonicalise.
    for backend, preds in per_backend.items():
        for p in preds:
            try:
                key = group_key(p.reactants)
                canon_reactants = key.split(".")
            except ValueError:
                log.debug("backend=%s invalid SMILES in prediction, skipping", backend)
                continue
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

    # Optional async features: scored in parallel across groups.
    rascore_tasks: dict[str, asyncio.Task[float | None]] = {}
    scscore_tasks: dict[str, asyncio.Task[float | None]] = {}
    rt_tasks: dict[str, asyncio.Task[bool]] = {}

    if rascorer is not None:
        for k, g in groups.items():
            rascore_tasks[k] = asyncio.create_task(rascorer(g.reactants))
    if scscorer is not None:
        for k, g in groups.items():
            scscore_tasks[k] = asyncio.create_task(scscorer(g.reactants))
    if forward_checker is not None:
        for k, g in groups.items():
            rt_tasks[k] = asyncio.create_task(forward_checker(canonical_target, g.reactants))

    results: list[MetaPrediction] = []
    for k, g in groups.items():
        rrf = reciprocal_rank_fusion(g.contributions, k=rrf_k)
        norm_scores = [normalise_score(b, p.score, mm) for b, p in g.contributions]
        mean_norm = sum(norm_scores) / len(norm_scores) if norm_scores else 0.0

        rascore_min = await rascore_tasks[k] if k in rascore_tasks else None
        scscore_max = await scscore_tasks[k] if k in scscore_tasks else None
        round_trip = await rt_tasks[k] if k in rt_tasks else None

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
