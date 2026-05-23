# Backend microservices

Every backend image follows the same pattern:

1. A `*.Dockerfile` that pins the backend's exact upstream dependencies
   (CUDA version, PyTorch pin, DGL pin, RDKit variant, etc.) and clones
   the upstream repo.
2. A `*_service.py` that imports the shared `_base.py` skeleton,
   subclasses `Backend`, and implements one or more of `predict()`,
   `forward()`, `plan()` against the upstream Python API.
3. An entry in `docker/compose.yaml` (or `compose.cpu.yaml` for
   lightweight backends).

The shared base in `_base.py` provides the uniform `/predict /forward
/plan /info /healthz` HTTP contract that the gateway expects (see
`chemclaw_retro/backends/remote.py`).

## Adding a new backend

```bash
# 1. Adapter module in the gateway (BackendInfo metadata only)
$EDITOR src/chemclaw_retro/backends/adapters/<name>.py

# 2. Microservice
$EDITOR docker/backends/<name>_service.py
$EDITOR docker/backends/<name>.Dockerfile

# 3. Compose entry + config endpoint
$EDITOR docker/compose.yaml
$EDITOR src/chemclaw_retro/config.py  # only if endpoint doesn't already exist

# 4. (Optional) Weight download
$EDITOR scripts/download_weights.sh
```

## Why one container per backend?

CUDA toolkit, PyTorch, DGL, OpenNMT, RDKit, transformers — every
backend pins different versions. Co-locating them in a single Python
environment is operationally hostile. Microservices keep the gateway
small and lets each backend evolve independently.
