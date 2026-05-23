"""Backend abstractions and per-engine adapters.

Adapters speak the uniform contract defined in ``base.py``; each is
deployed as its own microservice (see ``docker/backends/``) so that
conflicting Python / CUDA / DGL dependencies stay isolated.
"""
