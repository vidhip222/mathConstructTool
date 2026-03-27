#!/usr/bin/env bash
# =============================================================================
# pace/run_benchmark.sh — SLURM job: run MathConstruct benchmark (tool solver)
# =============================================================================
# Submit AFTER the vLLM server job is running:
#
#   VLLM_JOB_ID=$(sbatch --parsable pace/run_vllm_server.sh)
#   sbatch --dependency=after:${VLLM_JOB_ID} pace/run_benchmark.sh
#
# Or manually after server is up:
#   sbatch pace/run_benchmark.sh
#
# Adjust --partition and --account to match your PACE allocation.
# =============================================================================

#SBATCH --job-name=mathconstruct-tools
#SBATCH --partition=cpu-medium            # CPU node is fine for the client
#SBATCH --account=YOUR_PACE_ACCOUNT       # <-- replace with your PACE account
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/benchmark_%j.out
#SBATCH --error=logs/benchmark_%j.err

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

# --------------------------------------------------------------------------
# Wait for vLLM server to be ready
# --------------------------------------------------------------------------
# Read the GPU node hostname written by run_vllm_server.sh
VLLM_NODE_FILE="logs/vllm_node.txt"
MAX_WAIT=600   # wait up to 10 minutes for the server to start

echo "Waiting for vLLM server ..."
WAITED=0
while true; do
    if [[ -f "${VLLM_NODE_FILE}" ]]; then
        VLLM_NODE=$(cat "${VLLM_NODE_FILE}")
        VLLM_URL="http://${VLLM_NODE}:8000/v1"
        # Check if the server is responding
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
# Set environment variables
# --------------------------------------------------------------------------
export OPENAI_API_KEY="dummy-local"
export VLLM_BASE_URL="${VLLM_URL}"

# Patch the config to use the dynamic vLLM URL
# (Alternatively, edit configs/pace_llama_tools.yaml before submitting)
CONFIG_FILE="configs/pace_llama_tools.yaml"
TEMP_CONFIG=$(mktemp --suffix=.yaml)
sed "s|local_api_base_url:.*|local_api_base_url: \"${VLLM_URL}\"|" \
    "${CONFIG_FILE}" > "${TEMP_CONFIG}"

# --------------------------------------------------------------------------
# Run the benchmark
# --------------------------------------------------------------------------
echo "Starting MathConstruct benchmark ..."
echo "Config: ${TEMP_CONFIG}"
echo "Output: outputs/llama-tools-run/"

uv run python src/scripts/run.py "${TEMP_CONFIG}"

echo "Benchmark complete. Results in outputs/llama-tools-run/"

rm -f "${TEMP_CONFIG}"
