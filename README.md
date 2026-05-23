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
- **Backend adapters** — one Python module + one Docker image per
  retrosynthesis engine. Phase 1 ships RetroSim + AiZynthFinder +
  Chemformer forward, with scaffolding to plug in 30+ more engines.
- **Pluggable reranker** — heuristic by default; LightGBM-based learned
  reranker scaffolded under `training/reranker/`.

See [`/root/.claude/plans/perform-extensive-web-search-greedy-moth.md`](#)
for the full survey, design rationale, and backend catalogue.

## Quickstart (CPU only, no GPU needed)

```bash
# 1) Fetch model weights / templates / stock
bash scripts/download_weights.sh aizynth retrosim

# 2) Start gateway + AiZynthFinder backend
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

## Development

```bash
pip install -e ".[dev,scoring,aizynth,retrosim]"
pytest -q
ruff check src tests
mypy src
```

## License

MIT (this repo). Each wrapped backend retains its own license; see
`/backends` on the running gateway for the live list.
