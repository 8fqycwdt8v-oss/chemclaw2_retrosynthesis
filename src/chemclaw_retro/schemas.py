"""Pydantic models forming the contract between the gateway, backend
adapters, and the MCP tool surface.

Every field carries a ``description`` so that MCP clients (e.g. chemclaw2)
see useful tool schemas without us writing duplicate JSON-schema docs.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Backend = str
"""Short backend identifier, e.g. ``"aizynth"``, ``"retrosim"``."""


# ---------------------------------------------------------------------------
# Single-step
# ---------------------------------------------------------------------------


class SinglePrediction(BaseModel):
    """One backend's proposal for how to disconnect a target molecule."""

    model_config = ConfigDict(extra="forbid")

    reactants: list[str] = Field(
        ...,
        description=(
            "List of reactant SMILES that, joined and reacted, are proposed "
            "to yield the target product. Canonicalised by the gateway."
        ),
    )
    score: float = Field(
        ...,
        description=(
            "Backend-native confidence in this disconnection. Scales differ "
            "per backend; the aggregator does not assume comparability."
        ),
    )
    rank: int = Field(
        ...,
        ge=0,
        description="Rank within the backend's own top-K output (0 = best).",
    )
    template: str | None = Field(
        default=None,
        description="SMARTS template applied (template-based backends only).",
    )
    template_id: str | None = Field(
        default=None,
        description="Stable identifier of the template (where applicable).",
    )
    atom_mapping: str | None = Field(
        default=None,
        description=(
            "Atom-mapped reaction SMILES (reactants>>product), produced by "
            "the backend or by RXNMapper if missing."
        ),
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Backend-specific extras (logits, attention, etc.).",
    )


class BackendContribution(BaseModel):
    """How a single backend contributed to one aggregated MetaPrediction."""

    model_config = ConfigDict(extra="forbid")

    backend: Backend
    rank: int
    score: float
    template_id: str | None = None


class MetaPrediction(BaseModel):
    """Aggregated, deduped, reranked single-step proposal."""

    model_config = ConfigDict(extra="forbid")

    reactants: list[str] = Field(..., description="Canonical reactant SMILES (sorted).")
    final_score: float = Field(..., description="Aggregator's final score; higher = better.")
    consensus_count: int = Field(
        ..., ge=1, description="Number of distinct backends proposing this."
    )
    features: dict[str, float] = Field(
        default_factory=dict,
        description=(
            "Feature vector that drove the score: rrf_score, "
            "mean_norm_score, rascore_min, scscore_max, round_trip_ok, "
            "rxnfp_class_match. See meta.features for definitions."
        ),
    )
    round_trip_ok: bool | None = Field(
        default=None,
        description=(
            "True iff a forward model on `reactants` reproduces the target "
            "(canonical match). None if round-trip was skipped."
        ),
    )
    provenance: list[BackendContribution] = Field(
        default_factory=list,
        description="Per-backend contributions, ordered by their own score.",
    )


class SingleStepRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    smiles: str = Field(..., description="Target product SMILES.")
    top_k: int = Field(10, ge=1, le=100, description="Top-K aggregated results.")
    backends: list[Backend] | Literal["auto"] = Field(
        default="auto",
        description=("Subset of backends to query. 'auto' uses every enabled backend."),
    )
    return_provenance: bool = Field(
        True, description="Include per-backend contributions in the response."
    )
    run_round_trip: bool = Field(
        True,
        description=(
            "If true, run a forward model on each candidate's reactants and "
            "annotate / boost groups whose forward prediction matches the "
            "target product."
        ),
    )
    per_backend_top_k: int = Field(
        25,
        ge=1,
        le=200,
        description="Top-K requested from each backend before aggregation.",
    )


class SingleStepResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: str = Field(..., description="Canonical target SMILES.")
    results: list[MetaPrediction]
    backends_queried: list[Backend]
    backends_failed: list[Backend] = Field(
        default_factory=list,
        description="Backends that errored or timed out; partial results returned.",
    )
    degraded: bool = Field(
        False,
        description="True if any backend failed; the result is best-effort.",
    )


# ---------------------------------------------------------------------------
# Multi-step
# ---------------------------------------------------------------------------


class RouteStep(BaseModel):
    """One disconnection in a synthetic route."""

    model_config = ConfigDict(extra="forbid")

    product: str = Field(..., description="Product (intermediate) SMILES.")
    reactants: list[str]
    backend: Backend
    score: float
    round_trip_ok: bool | None = None


class Route(BaseModel):
    """A complete synthetic route from purchasable building blocks to target."""

    model_config = ConfigDict(extra="forbid")

    target: str
    steps: list[RouteStep]
    leaves: list[str] = Field(..., description="Leaf molecules (should be in stock).")
    in_stock_fraction: float = Field(
        ..., ge=0.0, le=1.0, description="Fraction of leaves that are in stock."
    )
    depth: int
    final_score: float
    planner: Backend
    features: dict[str, float] = Field(default_factory=dict)


class MultiStepRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    smiles: str
    max_depth: int = Field(6, ge=1, le=12)
    stock: str = Field("zinc", description="Stock identifier ('zinc' or custom).")
    planner: Literal[
        "auto", "aizynth", "syntheseus", "synplanner", "directmultistep", "retrosynformer"
    ] = "auto"
    top_k_routes: int = Field(5, ge=1, le=50)


class MultiStepResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: str
    routes: list[Route]
    planners_used: list[Backend]


# ---------------------------------------------------------------------------
# Forward
# ---------------------------------------------------------------------------


class ForwardRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reactants: list[str] = Field(..., min_length=1)
    top_k: int = Field(3, ge=1, le=20)


class ForwardProduct(BaseModel):
    model_config = ConfigDict(extra="forbid")

    smiles: str
    score: float


class ForwardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    products: list[ForwardProduct]
    backend: Backend


# ---------------------------------------------------------------------------
# Scoring / classification / conditions
# ---------------------------------------------------------------------------


class SynthScoreResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    smiles: str
    rascore: float | None = Field(None, description="Higher = more accessible.")
    scscore: float | None = Field(None, description="1.0-5.0; lower = simpler.")
    sascore: float | None = Field(None, description="1.0-10.0; lower = easier.")
    syba: float | None = Field(None, description=">0 = easy, <0 = hard.")


class ReactionClassifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rxn_smiles: str = Field(..., description="reactants>>products")


class ReactionClass(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rxn_smiles: str
    rxnfp_class: str | None = None
    rxnfp_confidence: float | None = None
    insight_name: str | None = Field(
        None, description="Rxn-INSIGHT named reaction (e.g. 'Suzuki coupling')."
    )
    insight_class: str | None = None


class Conditions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rxn_smiles: str
    catalysts: list[str] = Field(default_factory=list)
    solvents: list[str] = Field(default_factory=list)
    reagents: list[str] = Field(default_factory=list)
    temperature_c: float | None = None
    confidence: float | None = None


# ---------------------------------------------------------------------------
# Backend metadata
# ---------------------------------------------------------------------------


class BackendInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Backend
    family: Literal[
        "template",
        "transformer",
        "graph",
        "similarity",
        "llm",
        "hybrid",
        "planner",
        "biocatalysis",
        "scoring",
        "classification",
        "conditions",
        "forward",
    ]
    license: str
    citation: str | None = None
    version: str | None = None
    capabilities: list[
        Literal[
            "single_step",
            "multi_step",
            "forward",
            "score",
            "classify",
            "conditions",
        ]
    ] = Field(default_factory=list)
    url: str | None = None
    enabled: bool = True
    healthy: bool = True
