#!/usr/bin/env bash
# =============================================================================
# pace/run_cot_llama8b.sh — SLURM job: MathConstruct CoT benchmark (Llama 3.1 8B)
# =============================================================================
# Submit AFTER the server job is running:
#
#   SERVER_JOB=$(sbatch --parsable pace/server_llama8b.sh)
#   sbatch --dependency=after:${SERVER_JOB} pace/run_cot_llama8b.sh
#
# Adjust --account to match your PACE allocation.
# =============================================================================

#SBATCH --job-name=mc-cot-llama8b
#SBATCH --partition=cpu-medium
#SBATCH --account=YOUR_PACE_ACCOUNT       # <-- replace with your PACE account
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --output=logs/cot_llama8b_%j.out
#SBATCH --error=logs/cot_llama8b_%j.err

set -euo pipefail

mkdir -p logs outputs

module purge
module load anaconda3/2023.03

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate mathconstruct

export PATH="${HOME}/.local/minizinc/bin:$PATH"

# --------------------------------------------------------------------------
# Wait for vLLM server
# --------------------------------------------------------------------------
VLLM_NODE_FILE="logs/vllm_node_llama8b.txt"
MAX_WAIT=600

echo "Waiting for vLLM server ..."
WAITED=0
while true; do
    if [[ -f "${VLLM_NODE_FILE}" ]]; then
        VLLM_NODE=$(cat "${VLLM_NODE_FILE}")
        VLLM_URL="http://${VLLM_NODE}:8000/v1"
        if curl -sf "${VLLM_URL}/models" > /dev/null 2>&1; then
            echo "vLLM server is up at ${VLLM_URL}"
            break
        fi
    fi
    if [[ $WAITED -ge $MAX_WAIT ]]; then
        echo "ERROR: vLLM server did not start within ${MAX_WAIT}s. Exiting."
        exit 1
    fi
    sleep 10
    WAITED=$((WAITED + 10))
    echo "  ... waited ${WAITED}s"
done

# --------------------------------------------------------------------------
# Run CoT benchmark
# --------------------------------------------------------------------------
export OPENAI_API_KEY="dummy-local"

CONFIG_FILE="configs/pace_llama8b_cot.yaml"
TEMP_CONFIG=$(mktemp --suffix=.yaml)
sed "s|local_api_base_url:.*|local_api_base_url: \"${VLLM_URL}\"|" \
    "${CONFIG_FILE}" > "${TEMP_CONFIG}"

echo "Starting Llama 3.1 8B CoT benchmark ..."
uv run python src/scripts/run.py "${TEMP_CONFIG}"

echo "Done. Results in outputs/llama8b-cot-run/"
rm -f "${TEMP_CONFIG}"
