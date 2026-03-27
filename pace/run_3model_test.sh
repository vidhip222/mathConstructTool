#!/usr/bin/env bash
# =============================================================================
# pace/run_3model_test.sh — SLURM benchmark client for 3-model vLLM test
#
# Runs CoT + ReAct-tool configs for one model at a time.
# The vLLM server must already be running (submit run_vllm_server.sh first).
#
# Usage:
#   # 1. Submit a vLLM server job for the model you want, e.g.:
#   MODEL=llama8b sbatch pace/run_vllm_server.sh
#
#   # 2. Then submit this benchmark job, passing the model label:
#   MODEL_LABEL=llama8b sbatch --dependency=after:<SERVER_JOB_ID> pace/run_3model_test.sh
#
# MODEL_LABEL must be one of: llama8b | qwen32b | llama70b
# =============================================================================

#SBATCH --job-name=mc-3model-test
#SBATCH --partition=cpu-medium
#SBATCH --account=YOUR_PACE_ACCOUNT       # <-- replace
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=4:00:00
#SBATCH --output=logs/3model_%j.out
#SBATCH --error=logs/3model_%j.err

set -euo pipefail
mkdir -p logs outputs

# --------------------------------------------------------------------------
# Load environment
# --------------------------------------------------------------------------
module purge
module load anaconda3/2023.09
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate mathconstruct
export PATH="${HOME}/.local/minizinc/bin:$PATH"
export OPENAI_API_KEY="dummy-local"

# --------------------------------------------------------------------------
# Resolve vLLM URL (server writes its hostname to logs/vllm_node.txt)
# --------------------------------------------------------------------------
VLLM_NODE_FILE="logs/vllm_node.txt"
MAX_WAIT=600
WAITED=0
echo "Waiting for vLLM server..."
while true; do
    if [[ -f "${VLLM_NODE_FILE}" ]]; then
        VLLM_NODE=$(cat "${VLLM_NODE_FILE}")
        VLLM_URL="http://${VLLM_NODE}:8000/v1"
        if curl -sf "${VLLM_URL}/models" > /dev/null 2>&1; then
            echo "vLLM up at ${VLLM_URL}"
            break
        fi
    fi
    [[ $WAITED -ge $MAX_WAIT ]] && { echo "ERROR: server timeout"; exit 1; }
    sleep 10; WAITED=$((WAITED + 10))
    echo "  waited ${WAITED}s..."
done

# --------------------------------------------------------------------------
# Select configs based on MODEL_LABEL env var
# --------------------------------------------------------------------------
MODEL_LABEL="${MODEL_LABEL:-llama8b}"   # default to llama8b

case "${MODEL_LABEL}" in
    llama8b)
        COT_CFG="configs/vllm_test/cot_llama8b.yaml"
        TOOL_CFG="configs/vllm_test/tool_llama8b.yaml"
        ;;
    qwen32b)
        COT_CFG="configs/vllm_test/cot_qwen32b.yaml"
        TOOL_CFG="configs/vllm_test/tool_qwen32b.yaml"
        ;;
    llama70b)
        COT_CFG="configs/vllm_test/cot_llama70b.yaml"
        TOOL_CFG="configs/vllm_test/tool_llama70b.yaml"
        ;;
    *)
        echo "ERROR: Unknown MODEL_LABEL '${MODEL_LABEL}'. Use: llama8b | qwen32b | llama70b"
        exit 1
        ;;
esac

# Patch the vLLM URL into the configs
run_with_url() {
    local cfg="$1"
    local tmp; tmp=$(mktemp --suffix=.yaml)
    sed "s|local_api_base_url:.*|local_api_base_url: \"${VLLM_URL}\"|" "${cfg}" > "${tmp}"
    echo "--- Running: ${cfg} ---"
    uv run python src/scripts/run.py "${tmp}"
    rm -f "${tmp}"
}

# --------------------------------------------------------------------------
# Run CoT, then ReAct-tool
# --------------------------------------------------------------------------
run_with_url "${COT_CFG}"
run_with_url "${TOOL_CFG}"

echo "Done. Results in outputs/"
