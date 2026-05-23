# chemclaw2_retrosynthesis

Meta-model retrosynthesis **MCP server** built on FastAPI. Wraps every
truly open-source chemical retrosynthesis engine we could find
(template-based, template-free transformer, graph-based, LLM-based,
multi-step planners, biocatalysis, ...) and combines their predictions
into a single consensus answer with full per-backend provenance.

Consumed by the chemistry agent at
[`8fqycwdt8v-oss/chemclaw2`](https://github.com/8fqycwdt8v-oss/chemclaw2)
via standard MCP (Streamable HTTP).

## What's in the box

- **Gateway** — FastAPI app, auto-mounted as MCP via
  [`fastapi-mcp`](https://github.com/tadata-org/fastapi_mcp).
- **Meta-aggregator** — canonicalisation → grouping → reciprocal-rank
  fusion → RAscore / SCScore / round-trip boosts → top-K with
  provenance.
- **Backend microservices** — one Docker image per engine, each in its
  own conda env / CUDA pin / RDKit variant. Gateway never imports ML
  deps.
- **Pluggable reranker** — heuristic (default) or LightGBM-learned
  (Phase 4), behind a single `Reranker` interface.

## Wrapped backends (40+)

| Family | Backends |
|---|---|
| **Multi-step planners** | aizynth, askcos, syntheseus, synplanner, openretro, retrostar, desp, directmultistep, retrochimera, retrosynformer, ttl, deepretro, fusionretro |
| **Template** | localretro, mhnreact, neuralsym, retrocomposer |
| **Transformer** | chemformer, disconnection_chemformer, rsmiles, retroprime, retroformer, t5chem, tied_twoway, het_retro, retroxpert *(flagged)* |
| **Graph** | graph2smiles, megan, graphretro, retrobridge, gln, g2retro |
| **Similarity** | retrosim |
| **LLM** | rsgpt, chemdfm, batgpt, retrodfm |
| **Biocatalysis** | readretro, retrobiocat, retropath, enzyformer |

All under MIT / Apache-2.0 / BSD. `GET /backends` on the running
gateway returns the live status + license + citation for each.

## Quickstart (CPU only, no GPU needed)

```bash
# 1) Fetch model weights / templates / stock for Phase-1 set
bash scripts/download_weights.sh aizynth retrosim chemformer rascore

# 2) Start gateway + Phase-1 backends
docker compose -f docker/compose.cpu.yaml up -d --build

# 3) Health + introspection
curl -s http://localhost:8000/healthz
curl -s http://localhost:8000/backends | jq '.'

# 4) Run an ensemble single-step call
curl -s -X POST http://localhost:8000/retrosynthesis/single_step \
  -H 'content-type: application/json' \
  -d '{"smiles":"CC(=O)Oc1ccccc1C(=O)O","top_k":5,"run_round_trip":false}' \
  | jq '.'

# 5) Inspect the MCP surface chemclaw2 will see
npx @modelcontextprotocol/inspector --url http://localhost:8000/mcp
```

## Bring up more backends

Each non-Phase-1 backend is a Docker Compose service behind a profile.
After fetching that backend's weights:

```bash
# Phase 2: transformer + template + graph (GPU)
docker compose -f docker/compose.yaml --profile phase2 up -d --build

# Phase 3: heavy planners + LLMs (GPU, lots of disk)
docker compose -f docker/compose.yaml --profile phase3 up -d --build

# Phase 4: biocatalysis / natural products
docker compose -f docker/compose.yaml --profile phase4 up -d --build

# Or by family
docker compose -f docker/compose.yaml --profile template up -d --build
docker compose -f docker/compose.yaml --profile llm      up -d --build

# Enable each backend's adapter in the gateway by env var
CHEMCLAW_RETRO_BACKEND_LOCALRETRO__ENABLED=true \
CHEMCLAW_RETRO_BACKEND_CHEMFORMER__ENABLED=true \
docker compose up -d gateway
```

## Wire into chemclaw2

```jsonc
// chemclaw2/packages/mcp-servers/chemclaw-retro.json
{
  "mcpServers": {
    "chemclaw-retro": {
      "transport": "streamable-http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

See [`examples/chemclaw2_mcp_config.json`](examples/chemclaw2_mcp_config.json).

## MCP tools exposed

| Tool                          | Description                                              |
|-------------------------------|----------------------------------------------------------|
| `retrosynthesis_single_step`  | Ensemble single-step disconnection with provenance.      |
| `retrosynthesis_multi_step`   | Full retrosynthetic route to stock molecules.            |
| `reaction_forward`            | Predict products from reactants (round-trip helper).     |
| `reaction_classify`           | rxnfp + Rxn-INSIGHT reaction naming.                     |
| `reaction_conditions`         | Catalyst / solvent / reagent / temperature suggestions.  |
| `score_synthesizability`      | RAscore + SCScore + SAscore for one molecule.            |
| `backends_list`               | List enabled backends, licenses, capabilities, health.   |
| `healthz`, `version`          | Liveness probes.                                         |

## Learned reranker (Phase 4)

The default heuristic reranker uses reciprocal-rank fusion + consensus
+ RAscore + round-trip. Once enough backends are live to make ensemble
training data informative, train a LightGBM reranker:

```bash
# Replay USPTO-50K through the running gateway → feature dataset
python -m training.reranker.build_dataset \
    --tsv data/uspto_50k_test.tsv --out training/reranker/dataset.parquet

# Train + export
python -m training.reranker.train_lightgbm

# Switch the gateway over
export CHEMCLAW_RETRO_RERANKER=learned
export CHEMCLAW_RETRO_LEARNED_MODEL=training/reranker/model.joblib
docker compose restart gateway
```

See [`training/reranker/README.md`](training/reranker/README.md).

## Development

```bash
pip install -e ".[dev,scoring,aizynth,retrosim,training]"
pytest -q
ruff check src tests
mypy src
```

## Design plan

The full survey + design rationale + backend catalogue is in the saved
plan at `/root/.claude/plans/perform-extensive-web-search-greedy-moth.md`
(checked into your local Claude session).

## License

MIT (this repo). Each wrapped backend retains its own license; see
`/backends` on the running gateway for the live list.
