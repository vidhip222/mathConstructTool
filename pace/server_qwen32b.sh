#!/usr/bin/env bash
#SBATCH --job-name=vllm-qwen32b
#SBATCH --partition=gpu-a100-40
#SBATCH --account=YOUR_PACE_ACCOUNT
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=80G
#SBATCH --gres=gpu:A100:2
#SBATCH --time=6:00:00
#SBATCH --output=logs/vllm_qwen32b_%j.out
#SBATCH --error=logs/vllm_qwen32b_%j.err

set -euo pipefail
mkdir -p logs

module purge
module load anaconda3/2023.03
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate mathconstruct

# HuggingFace cache — point to scratch to avoid home quota
# Replace X with the first letter of your username (e.g. /storage/scratch1/v/vpatra3/hf_cache)
export HF_HOME=/storage/scratch1/X/YOUR_USERNAME/hf_cache
export HF_HUB_DISABLE_XET=1

echo "$(hostname)" > logs/vllm_node_qwen32b.txt
echo "Starting vLLM for Qwen2.5-32B on $(hostname):8000"

python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-32B-Instruct \
    --tensor-parallel-size 2 \
    --dtype bfloat16 \
    --port 8000 \
    --host 0.0.0.0 \
    --max-model-len 8192 \
    --trust-remote-code \
    --uvicorn-log-level warning
