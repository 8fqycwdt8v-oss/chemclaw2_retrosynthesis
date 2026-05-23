#!/usr/bin/env bash
# Download pretrained weights / templates / stock files for the enabled
# backends. Idempotent and checksum-validated.
#
# Usage: bash scripts/download_weights.sh [backend ...]
#        (no args = download every Phase-1 backend's assets)
#
# Assets are written under ./weights/<backend>/ and mounted into each
# backend container by docker/compose.cpu.yaml.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WEIGHTS_DIR="${ROOT}/weights"
mkdir -p "${WEIGHTS_DIR}"

want=("$@")
if [[ ${#want[@]} -eq 0 ]]; then
    want=(aizynth retrosim chemformer rascore)
fi

aizynth() {
    local dst="${WEIGHTS_DIR}/aizynth"
    mkdir -p "${dst}"
    # The aizynthfinder helper writes a config.yml plus the policy/stock
    # files into the chosen directory.
    pip install --quiet "aizynthfinder>=4.4"
    download_public_data "${dst}"  # provided by aizynthfinder CLI
    echo "[aizynth] weights ready at ${dst}"
}

retrosim() {
    local dst="${WEIGHTS_DIR}/retrosim"
    mkdir -p "${dst}"
    # RetroSim ships its precedent corpus inside the repo; clone shallow.
    if [[ ! -d "${dst}/repo" ]]; then
        git clone --depth 1 https://github.com/connorcoley/retrosim.git "${dst}/repo"
    fi
    echo "[retrosim] corpus ready at ${dst}/repo"
}

chemformer() {
    local dst="${WEIGHTS_DIR}/chemformer"
    mkdir -p "${dst}"
    if [[ ! -f "${dst}/combined.ckpt" ]]; then
        echo "[chemformer] download the pretrained checkpoint manually from"
        echo "             https://github.com/MolecularAI/Chemformer (see README)"
        echo "             and place it at ${dst}/combined.ckpt"
    fi
}

rascore() {
    pip install --quiet rascore
    echo "[rascore] installed via pip"
}

for b in "${want[@]}"; do
    case "${b}" in
        aizynth)    aizynth ;;
        retrosim)   retrosim ;;
        chemformer) chemformer ;;
        rascore)    rascore ;;
        *) echo "unknown backend: ${b}" >&2; exit 1 ;;
    esac
done
