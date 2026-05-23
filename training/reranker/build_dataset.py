"""Replay USPTO-50K (or any ``product\treactants`` TSV) through every
enabled backend, extract the meta-aggregator's feature vectors, and
label each prediction 1 if its canonical reactant set matches the
ground-truth, else 0.

Output: a parquet file `dataset.parquet` with columns
[target, group_key, label, rrf_score, consensus_count, mean_norm_score,
rascore_min, scscore_max, round_trip_ok, rxnfp_class_match].

Usage:
    python -m training.reranker.build_dataset \\
        --tsv data/uspto_50k_test.tsv \\
        --out training/reranker/dataset.parquet \\
        --gateway-url http://localhost:8000
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path

import httpx

log = logging.getLogger(__name__)


async def _call_gateway(client: httpx.AsyncClient, url: str, smiles: str, top_k: int) -> dict:
    resp = await client.post(
        f"{url}/retrosynthesis/single_step",
        json={"smiles": smiles, "top_k": top_k, "run_round_trip": True, "return_provenance": True},
        timeout=300.0,
    )
    resp.raise_for_status()
    return resp.json()


async def main(args: argparse.Namespace) -> None:
    from chemclaw_retro.canonical import group_key  # local import to keep CLI light

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    async with httpx.AsyncClient() as client:
        with open(args.tsv) as f:
            for line_no, line in enumerate(f):
                if line_no >= args.limit:
                    break
                target, ground = line.strip().split("\t", 1)
                try:
                    data = await _call_gateway(client, args.gateway_url, target, args.top_k)
                except Exception as e:
                    log.warning("gateway call failed for %s: %s", target, e)
                    continue
                truth_key = group_key(ground.split("."))
                for r in data.get("results", []):
                    rec_key = group_key(r["reactants"])
                    records.append(
                        {
                            "target": data["target"],
                            "group_key": rec_key,
                            "label": int(rec_key == truth_key),
                            **r.get("features", {}),
                        }
                    )

    if not records:
        raise SystemExit("no records collected; check the gateway and TSV")

    try:
        import pandas as pd

        df = pd.DataFrame(records).fillna(0.0)
        df.to_parquet(out_path)
        print(f"wrote {len(df)} rows to {out_path}")
    except ImportError:
        # Fallback: JSONL if pandas isn't installed.
        with out_path.with_suffix(".jsonl").open("w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        print(f"wrote {len(records)} rows to {out_path.with_suffix('.jsonl')}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--tsv", required=True, help="TSV with target<TAB>reactants per line")
    p.add_argument("--out", default="training/reranker/dataset.parquet")
    p.add_argument("--gateway-url", default="http://localhost:8000")
    p.add_argument("--top-k", type=int, default=25)
    p.add_argument("--limit", type=int, default=5000)
    return p.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(parse_args()))
