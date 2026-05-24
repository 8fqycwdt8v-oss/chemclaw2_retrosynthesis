"""Train a LightGBM ranker over the dataset produced by
``build_dataset.py``. Output: ``model.joblib`` loadable by
:class:`chemclaw_retro.meta.learned_reranker.LearnedReranker`.

Usage:
    python -m training.reranker.train_lightgbm \\
        --dataset training/reranker/dataset.parquet \\
        --out training/reranker/model.joblib
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from chemclaw_retro.meta.learned_reranker import FEATURE_ORDER

log = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> None:
    import joblib
    import lightgbm as lgb
    import pandas as pd
    from sklearn.metrics import average_precision_score
    from sklearn.model_selection import train_test_split

    df = pd.read_parquet(args.dataset)
    # reindex (not df[FEATURE_ORDER]) so missing columns fill with 0.0
    # instead of KeyError-ing. Optional features (rxnfp_class_match,
    # round_trip_ok, rascore_min, scscore_max) may be absent from the
    # dataset if the gateway had those components disabled when the
    # dataset was built.
    missing = [c for c in FEATURE_ORDER if c not in df.columns]
    if missing:
        log.warning("dataset missing features %s; filling with 0.0", missing)
    X = df.reindex(columns=FEATURE_ORDER, fill_value=0.0).fillna(0.0).to_numpy()
    y = df["label"].to_numpy()

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
    model = lgb.LGBMClassifier(
        n_estimators=400,
        learning_rate=0.05,
        max_depth=-1,
        num_leaves=63,
        reg_lambda=1.0,
        objective="binary",
        n_jobs=-1,
    )
    model.fit(Xtr, ytr, eval_set=[(Xte, yte)], callbacks=[lgb.early_stopping(20)])

    probs = model.predict_proba(Xte)[:, 1]
    ap = average_precision_score(yte, probs)
    print(f"validation AP = {ap:.4f}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_path)
    print(f"saved model to {out_path}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="training/reranker/dataset.parquet")
    p.add_argument("--out", default="training/reranker/model.joblib")
    return p.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(parse_args())
