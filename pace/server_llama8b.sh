#!/usr/bin/env bash
#SBATCH --job-name=vllm-llama8b
#SBATCH --partition=gpu-a100-40
#SBATCH --account=YOUR_PACE_ACCOUNT
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --gres=gpu:A100:1
#SBATCH --time=4:00:00
#SBATCH --output=logs/vllm_llama8b_%j.out
#SBATCH --error=logs/vllm_llama8b_%j.err

set -euo pipefail
mkdir -p logs

module purge
module load anaconda3/2023.09
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate mathconstruct

echo "$(hostname)" > logs/vllm_node.txt
echo "Starting vLLM for Llama 3.1 8B on $(hostname):8000"

python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --tensor-parallel-size 1 \
    --dtype bfloat16 \
    --port 8000 \
    --host 0.0.0.0 \
    --max-model-len 8192 \
    --trust-remote-code \
    --uvicorn-log-level warning
