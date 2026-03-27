#!/usr/bin/env bash
# =============================================================================
# pace/setup_env.sh — Set up the MathConstruct environment on PACE Phoenix
# =============================================================================
# Run this ONCE on a PACE login node before submitting any jobs.
#
# Usage:
#   chmod +x pace/setup_env.sh
#   ./pace/setup_env.sh
# =============================================================================

set -euo pipefail

CONDA_ENV_NAME="mathconstruct"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== MathConstruct PACE Setup ==="
echo "Project dir: $PROJECT_DIR"

# --------------------------------------------------------------------------
# 1. Load modules (PACE Phoenix)
# --------------------------------------------------------------------------
module purge
module load anaconda3/2023.03        # or latest available: module avail anaconda
module load gcc/12.3.0               # needed for some C-extension packages

echo "[1/7] Modules loaded."

# --------------------------------------------------------------------------
# 2. Create conda environment
# --------------------------------------------------------------------------
if conda env list | grep -q "^${CONDA_ENV_NAME}"; then
    echo "[2/7] Conda env '${CONDA_ENV_NAME}' already exists, skipping creation."
else
    conda create -y -n "${CONDA_ENV_NAME}" python=3.12
    echo "[2/7] Conda env '${CONDA_ENV_NAME}' created."
fi

# Activate
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "${CONDA_ENV_NAME}"

# --------------------------------------------------------------------------
# 3. Install uv (fast package manager used by the project)
# --------------------------------------------------------------------------
pip install --quiet uv
echo "[3/7] uv installed."

# --------------------------------------------------------------------------
# 4. Install project dependencies (uv respects pyproject.toml)
# --------------------------------------------------------------------------
cd "$PROJECT_DIR"
uv pip install -e .
echo "[4/7] Project dependencies installed."

# --------------------------------------------------------------------------
# 5. Install free math solver tools
# --------------------------------------------------------------------------
pip install --quiet \
    z3-solver \
    ortools \
    pycryptosat \
    networkx \
    sympy \
    scipy \
    numpy \
    vllm \
    openai

echo "[5/7] Python solver packages installed (z3, ortools, pycryptosat, networkx, sympy, vllm)."

# --------------------------------------------------------------------------
# 6. MiniZinc binary (user-space install)
# --------------------------------------------------------------------------
MINIZINC_VERSION="2.8.5"
MINIZINC_DIR="${HOME}/.local/minizinc"

if command -v minizinc &>/dev/null; then
    echo "[6/7] MiniZinc already on PATH, skipping."
else
    echo "[6/7] Installing MiniZinc ${MINIZINC_VERSION} ..."
    mkdir -p "${MINIZINC_DIR}"
    wget -q "https://github.com/MiniZinc/MiniZincIDE/releases/download/${MINIZINC_VERSION}/MiniZincIDE-${MINIZINC_VERSION}-bundle-linux-x86_64.tgz" \
        -O /tmp/minizinc.tgz
    tar -xzf /tmp/minizinc.tgz -C "${MINIZINC_DIR}" --strip-components=1
    rm /tmp/minizinc.tgz

    # Add to shell profile
    LINE="export PATH=\"${MINIZINC_DIR}/bin:\$PATH\""
    grep -qxF "$LINE" "${HOME}/.bashrc" || echo "$LINE" >> "${HOME}/.bashrc"
    export PATH="${MINIZINC_DIR}/bin:$PATH"
    echo "[6/7] MiniZinc installed at ${MINIZINC_DIR}/bin/minizinc"
fi

# --------------------------------------------------------------------------
# 7. GAP system (optional — install via spack or module if available)
# --------------------------------------------------------------------------
if command -v gap &>/dev/null; then
    echo "[7/7] GAP already on PATH."
elif module avail gap 2>&1 | grep -q gap; then
    echo "[7/7] GAP module available — add 'module load gap' to your job scripts."
else
    echo "[7/7] GAP not found. Install via: conda install -c conda-forge gap-system"
    echo "       Or load the module: module load gap (if available on your cluster)."
fi

# --------------------------------------------------------------------------
# SageMath (optional — large)
# --------------------------------------------------------------------------
# Uncomment if SageMath is needed:
# conda install -y -c conda-forge sage

# --------------------------------------------------------------------------
# Lean 4 (optional — for formal proof checking)
# --------------------------------------------------------------------------
if command -v lean &>/dev/null; then
    echo "[opt] Lean 4 already on PATH."
else
    echo "[opt] To install Lean 4, run:"
    echo "       curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh"
    echo "       Then: elan default leanprover/lean4:stable"
fi

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "  1. Set your API keys (only OPENAI_API_KEY=dummy needed for local vLLM):"
echo "       export OPENAI_API_KEY=dummy"
echo "  2. Download Llama 3.3 70B weights (requires HuggingFace access):"
echo "       huggingface-cli download meta-llama/Llama-3.3-70B-Instruct"
echo "  3. Submit the vLLM server job:"
echo "       sbatch pace/run_vllm_server.sh"
echo "  4. After server is up, submit the benchmark job:"
echo "       sbatch pace/run_benchmark.sh"
