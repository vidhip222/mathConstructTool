#!/usr/bin/env bash
# =============================================================================
# pace/run_interactive.sh — Run vLLM server + benchmarks on an interactive GPU node
#
# Usage:
#   bash pace/run_interactive.sh [MODEL]
#
# MODEL options:
#   8b    — Llama 3.1 8B  (1 GPU)
#   32b   — Qwen2.5 32B   (2 GPUs)
#   70b   — Llama 3.3 70B (4 GPUs)  [default]
#
# Example:
#   bash pace/run_interactive.sh 70b
# =============================================================================

set -euo pipefail

MODEL="${1:-70b}"

# --------------------------------------------------------------------------
# Config per model
# --------------------------------------------------------------------------
case "$MODEL" in
    8b)
        MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"
        TENSOR_PARALLEL=1
        DTYPE="half"
        VLLM_EXTRA_FLAGS=""
        COT_CONFIG="configs/pace_llama8b_cot.yaml"
        TOOL_CONFIG="configs/pace_llama8b_tool.yaml"
        COT_OUT="outputs/llama8b-cot-run"
        TOOL_OUT="outputs/llama8b-tool-run"
        ;;
    32b)
        MODEL_NAME="Qwen/Qwen2.5-32B-Instruct"
        TENSOR_PARALLEL=2
        DTYPE="bfloat16"
        VLLM_EXTRA_FLAGS=""
        COT_CONFIG="configs/pace_qwen32b_cot.yaml"
        TOOL_CONFIG="configs/pace_qwen32b_tool.yaml"
        COT_OUT="outputs/qwen32b-cot-run"
        TOOL_OUT="outputs/qwen32b-tool-run"
        ;;
    70b)
        MODEL_NAME="meta-llama/Llama-3.3-70B-Instruct"
        TENSOR_PARALLEL=4
        DTYPE="bfloat16"
        VLLM_EXTRA_FLAGS="--enable-auto-tool-choice --tool-call-parser llama3_json"
        COT_CONFIG="configs/pace_llama_cot.yaml"
        TOOL_CONFIG="configs/pace_llama_tools.yaml"
        COT_OUT="outputs/llama-cot-run"
        TOOL_OUT="outputs/llama-tools-run"
        ;;
    *)
        echo "ERROR: Unknown model '${MODEL}'. Use: 8b, 32b, or 70b"
        exit 1
        ;;
esac

# --------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------
module purge
module load anaconda3/2023.03
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate mathconstruct

export PATH="${HOME}/.local/minizinc/bin:$PATH"
export OPENAI_API_KEY="dummy-local"

# Set HF cache to scratch (edit username/letter as needed)
FIRST_LETTER="${USER:0:1}"
export HF_HOME="/storage/scratch1/${FIRST_LETTER}/${USER}/hf_cache"
export HF_HUB_DISABLE_XET=1

mkdir -p logs outputs

# --------------------------------------------------------------------------
# Start vLLM server in background
# --------------------------------------------------------------------------
echo "[1/3] Starting vLLM server for ${MODEL_NAME} ..."

python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL_NAME}" \
    --tensor-parallel-size "${TENSOR_PARALLEL}" \
    --dtype "${DTYPE}" \
    --port 8000 \
    --host 0.0.0.0 \
    --max-model-len 8192 \
    --trust-remote-code \
    ${VLLM_EXTRA_FLAGS} \
    > logs/vllm_${MODEL}.out 2>&1 &

VLLM_PID=$!
echo "vLLM PID: ${VLLM_PID} (logs: logs/vllm_${MODEL}.out)"

# Kill server on exit/ctrl-c
trap "echo 'Shutting down vLLM server...'; kill ${VLLM_PID} 2>/dev/null; exit" EXIT INT TERM

# --------------------------------------------------------------------------
# Wait for server to be ready
# --------------------------------------------------------------------------
echo "Waiting for vLLM server at http://localhost:8000/v1 ..."
MAX_WAIT=600
WAITED=0
while true; do
    if curl -sf http://localhost:8000/v1/models > /dev/null 2>&1; then
        echo "vLLM server is ready."
        break
    fi
    if [[ $WAITED -ge $MAX_WAIT ]]; then
        echo "ERROR: vLLM server did not start within ${MAX_WAIT}s."
        echo "Check logs/vllm_${MODEL}.out for details."
        exit 1
    fi
    sleep 10
    WAITED=$((WAITED + 10))
    echo "  ... waited ${WAITED}s"
done

# --------------------------------------------------------------------------
# Run CoT benchmark
# --------------------------------------------------------------------------
echo ""
echo "[2/3] Running CoT benchmark (config: ${COT_CONFIG}) ..."
uv run python src/scripts/run.py "${COT_CONFIG}"
echo "CoT done. Results in ${COT_OUT}"

# --------------------------------------------------------------------------
# Run tool benchmark
# --------------------------------------------------------------------------
echo ""
echo "[3/3] Running tool benchmark (config: ${TOOL_CONFIG}) ..."
uv run python src/scripts/run.py "${TOOL_CONFIG}"
echo "Tool done. Results in ${TOOL_OUT}"

# --------------------------------------------------------------------------
# Analyze
# --------------------------------------------------------------------------
echo ""
echo "Analyzing results ..."
uv run python src/scripts/analyze.py --run "${COT_OUT}"
uv run python src/scripts/analyze.py --run "${TOOL_OUT}"

echo ""
echo "All done!"
