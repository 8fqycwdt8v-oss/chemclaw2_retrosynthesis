# Learned reranker

Phase-4 feature. The default heuristic reranker (weights in
`src/chemclaw_retro/meta/weights.yaml`) is solid out of the box; the
learned reranker is a follow-up upgrade once enough backends are
running to make the consensus signal informative.

## Pipeline

```bash
# 1. Build a training set from USPTO-50K test split by replaying it
#    through the gateway. Requires the gateway to be running with
#    several backends enabled.
python -m training.reranker.build_dataset \
    --tsv data/uspto_50k_test.tsv \
    --out training/reranker/dataset.parquet \
    --gateway-url http://localhost:8000

# 2. Train a LightGBM ranker.
python -m training.reranker.train_lightgbm \
    --dataset training/reranker/dataset.parquet \
    --out training/reranker/model.joblib

# 3. Use it.
export CHEMCLAW_RETRO_RERANKER=learned
export CHEMCLAW_RETRO_LEARNED_MODEL=$PWD/training/reranker/model.joblib
docker compose -f docker/compose.yaml restart gateway
```

## Why LightGBM, not a neural reranker?

The feature vector is small (≤10 dims) and the dataset modest (≤500K
groups). LightGBM trains in seconds, has no GPU need, exports cleanly
to ONNX/joblib, and beats deeper models on tabular ranking at this
scale. The Chimera paper uses a heavier neural reranker — that's a
sensible v3.
