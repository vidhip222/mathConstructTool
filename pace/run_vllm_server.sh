#!/usr/bin/env bash
# =============================================================================
# pace/run_vllm_server.sh — SLURM job: serve Llama 3.3 70B via vLLM
# =============================================================================
# Submit with: sbatch pace/run_vllm_server.sh
#
# This job:
#   1. Loads the conda environment
#   2. Starts vLLM on port 8000 serving Llama 3.3 70B
#   3. Writes the GPU node hostname to a file so the benchmark job can find it
#   4. Runs until cancelled (the benchmark job depends on this job staying alive)
#
# Adjust --partition, --account, and --gres to match your PACE allocation.
# =============================================================================

#SBATCH --job-name=vllm-llama33
#SBATCH --partition=gpu-a100-40           # or gpu-a100-80, gpu-v100, etc.
#SBATCH --account=YOUR_PACE_ACCOUNT       # <-- replace with your PACE account
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=80G                         # 70B in fp16 needs ~140 GB; use fp8 or int4 for 80 GB
#SBATCH --gres=gpu:A100:2                 # 2x A100 40 GB for tensor parallelism
#SBATCH --time=12:00:00
#SBATCH --output=logs/vllm_%j.out
#SBATCH --error=logs/vllm_%j.err

set -euo pipefail

mkdir -p logs

# --------------------------------------------------------------------------
# Load environment
# --------------------------------------------------------------------------
module purge
module load anaconda3/2023.09

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate mathconstruct

export PATH="${HOME}/.local/minizinc/bin:$PATH"

# --------------------------------------------------------------------------
# Write this node's hostname so the benchmark job can connect
# --------------------------------------------------------------------------
NODE_HOSTNAME=$(hostname)
echo "${NODE_HOSTNAME}" > logs/vllm_node.txt
echo "vLLM will start on: ${NODE_HOSTNAME}:8000"

# --------------------------------------------------------------------------
# Model settings
# --------------------------------------------------------------------------
MODEL="meta-llama/Llama-3.3-70B-Instruct"
PORT=8000
TENSOR_PARALLEL=2          # match number of GPUs requested above

# --------------------------------------------------------------------------
# Start vLLM server
# --------------------------------------------------------------------------
# --dtype float16: standard precision (use bfloat16 if A100)
# --max-model-len: context window (reduce if OOM)
# --enable-auto-tool-choice + --tool-call-parser: enable function calling
python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL}" \
    --tensor-parallel-size "${TENSOR_PARALLEL}" \
    --dtype bfloat16 \
    --port "${PORT}" \
    --host 0.0.0.0 \
    --max-model-len 8192 \
    --enable-auto-tool-choice \
    --tool-call-parser llama3_json \
    --trust-remote-code \
    --uvicorn-log-level warning

# The server runs indefinitely until the SLURM job is cancelled.
