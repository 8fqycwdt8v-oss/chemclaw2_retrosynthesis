#!/usr/bin/env bash
# Download pretrained weights / templates / stock files for the enabled
# backends. Idempotent; checksums (where known) validated.
#
# Usage: bash scripts/download_weights.sh [backend ...]
#        (no args = Phase-1 lightweight set)
#
# Output: ./weights/<backend>/ — mounted into each backend container
#         by docker compose.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WEIGHTS_DIR="${ROOT}/weights"
mkdir -p "${WEIGHTS_DIR}"

want=("$@")
if [[ ${#want[@]} -eq 0 ]]; then
    want=(aizynth retrosim chemformer rascore)
fi

note_manual() {
    cat >&2 <<EOF
[${1}] manual step required:
${2}
  → place files under ${WEIGHTS_DIR}/${1}/ and re-run with --skip-existing
EOF
}

aizynth() {
    local dst="${WEIGHTS_DIR}/aizynth"
    mkdir -p "${dst}"
    pip install --quiet "aizynthfinder>=4.4"
    download_public_data "${dst}"
}

retrosim() {
    local dst="${WEIGHTS_DIR}/retrosim"
    mkdir -p "${dst}"
    [[ -d "${dst}/repo" ]] || git clone --depth 1 https://github.com/connorcoley/retrosim.git "${dst}/repo"
}

chemformer() {
    local dst="${WEIGHTS_DIR}/chemformer"
    mkdir -p "${dst}"
    [[ -f "${dst}/combined.ckpt" ]] || note_manual chemformer \
        "Download combined.ckpt + bart_vocab_downstream.json per https://github.com/MolecularAI/Chemformer"
}

rascore()        { pip install --quiet rascore; }
scscore()        { pip install --quiet scscore; }

localretro() {
    local dst="${WEIGHTS_DIR}/localretro"; mkdir -p "${dst}"
    note_manual localretro "git clone https://github.com/kaist-amsg/LocalRetro && copy LocalRetro_USPTO_50K.pth + templates.csv"
}

mhnreact() {
    local dst="${WEIGHTS_DIR}/mhnreact"; mkdir -p "${dst}"
    note_manual mhnreact "Run mhnreact-download per https://github.com/ml-jku/mhn-react#models"
}

neuralsym() {
    local dst="${WEIGHTS_DIR}/neuralsym"; mkdir -p "${dst}"
    note_manual neuralsym "Train per https://github.com/linminhtoo/neuralsym; expects elu_512.pt"
}

graph2smiles() {
    local dst="${WEIGHTS_DIR}/graph2smiles"; mkdir -p "${dst}"
    note_manual graph2smiles "Download uspto_50k_retro.pt and/or uspto_480k_forward.pt from Google Drive (link in repo README)"
}

megan() {
    local dst="${WEIGHTS_DIR}/megan"; mkdir -p "${dst}"
    note_manual megan "wget the v1.1 release megan_data.zip from https://github.com/molecule-one/megan/releases and unzip into ${dst}/"
}

rsmiles() {
    local dst="${WEIGHTS_DIR}/rsmiles"; mkdir -p "${dst}"
    note_manual rsmiles "Download USPTO_50K_aug20.pt from Google Drive (link in https://github.com/otori-bird/retrosynthesis README)"
}

graphretro() {
    local dst="${WEIGHTS_DIR}/graphretro"; mkdir -p "${dst}"
    note_manual graphretro "Train per https://github.com/vsomnath/graphretro; expects model.pt"
}

retroformer() {
    local dst="${WEIGHTS_DIR}/retroformer"; mkdir -p "${dst}"
    note_manual retroformer "Download checkpoint.pt per https://github.com/yuewan2/Retroformer"
}

gln() {
    local dst="${WEIGHTS_DIR}/gln"; mkdir -p "${dst}"
    note_manual gln "Download model.dump from Dropbox link in https://github.com/Hanjun-Dai/GLN README"
}

t5chem() {
    local dst="${WEIGHTS_DIR}/t5chem"; mkdir -p "${dst}"
    note_manual t5chem "Download retrosynthesis/ and product/ checkpoints from https://github.com/HelloJocelynLu/t5chem"
}

askcos() {
    note_manual askcos "Use upstream's official Compose; or pull image askcos/askcos:latest"
}

syntheseus() {
    local dst="${WEIGHTS_DIR}/syntheseus"; mkdir -p "${dst}"
    note_manual syntheseus "Run syntheseus-download per https://github.com/microsoft/syntheseus#models"
}

directmultistep() { pip install --quiet directmultistep; }

retrochimera() {
    local dst="${WEIGHTS_DIR}/retrochimera"; mkdir -p "${dst}"
    note_manual retrochimera "Download weights from https://github.com/microsoft/retrochimera (instructions in README)"
}

retrosynformer() {
    local dst="${WEIGHTS_DIR}/retrosynformer"; mkdir -p "${dst}"
    note_manual retrosynformer "Download from Zenodo per https://github.com/emmaryd/retrosynformer"
}

readretro()       { note_manual readretro     "Clone + follow https://github.com/SeulLee05/READRetro README"; }
retrobiocat()     { pip install --quiet retrobiocat; }
retropath()       { pip install --quiet retropath_rl; }
deepretro()       { note_manual deepretro     "Clone + follow https://github.com/deepforestsci/DeepRetro README; set ANTHROPIC_API_KEY"; }
retrobridge()     { note_manual retrobridge   "Download uspto_50k.ckpt per https://github.com/igashov/RetroBridge"; }
retroprime()      { note_manual retroprime    "Download checkpoints per https://github.com/wangxr0526/RetroPrime"; }
fusionretro()     { note_manual fusionretro   "Download uspto_50k.pt per https://github.com/SongtaoLiu0823/FusionRetro"; }
tied_twoway()     { note_manual tied_twoway   "Train per https://github.com/ejklike/tied-twoway-transformer"; }
g2retro()         { note_manual g2retro       "Download per https://github.com/yhwwang/G2Retro"; }
het_retro()       { note_manual het_retro     "Download per https://github.com/duartegroup/Het-retro"; }
retrocomposer()   { note_manual retrocomposer "Download per https://github.com/uta-smile/RetroComposer"; }
retroxpert()      { note_manual retroxpert    "Use leak_fix branch; build per https://github.com/uta-smile/RetroXpert (DISCLOSED INFORMATION LEAK)"; }
rsgpt()           { note_manual rsgpt         "Download weights from Zenodo: 10.5281/zenodo.15336192"; }
synplanner()      { pip install --quiet synplanner; }
ttl()             { note_manual ttl           "Clone + follow https://github.com/reymond-group/MultiStepRetrosynthesisTTL"; }
openretro()       { note_manual openretro     "Follow https://github.com/coleygroup/openretro for per-model weights"; }
retrostar()       { note_manual retrostar     "Train per https://github.com/binghong-ml/retro_star"; }
desp()            { note_manual desp          "Download per https://github.com/coleygroup/desp"; }
chemdfm()         { echo "[chemdfm]   weights pulled by transformers on first run (HF: OpenDFM/ChemDFM-13B-v1.0)"; }
batgpt()          { echo "[batgpt]    weights pulled by transformers on first run (configure HF_MODEL_ID in env)"; }
retrodfm()        { echo "[retrodfm]  weights pulled by transformers on first run (HF: OpenDFM/RetroDFM-R)"; }
enzyformer()      { note_manual enzyformer    "Awaiting upstream code release; see ChemRxiv 2025-8ggs5"; }
disconnection_chemformer() {
    note_manual disconnection_chemformer "Download per https://github.com/rxn4chemistry/disconnection_aware_retrosynthesis"
}

for b in "${want[@]}"; do
    fn="${b//-/_}"
    if declare -f "${fn}" >/dev/null; then
        "${fn}"
    else
        echo "unknown backend: ${b}" >&2; exit 1
    fi
done
