#!/usr/bin/env bash
# =============================================================================
# pace/vllm_server_configs.sh
#
# Template vLLM server commands for the 3 test models.
# Copy the relevant block into run_vllm_server.sh (or a new script) before
# submitting to SLURM.
#
# All models are open-weight (free via HuggingFace) — no API keys needed.
# =============================================================================

# ── Llama 3.1 8B ─────────────────────────────────────────────────────────────
# SLURM: --gres=gpu:A100:1  --mem=24G  --time=6:00:00
MODEL="meta-llama/Llama-3.1-8B-Instruct"
python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL}" \
    --tensor-parallel-size 1 \
    --dtype bfloat16 \
    --port 8000 \
    --host 0.0.0.0 \
    --max-model-len 8192 \
    --trust-remote-code \
    --uvicorn-log-level warning

# ── Qwen2.5 32B ──────────────────────────────────────────────────────────────
# SLURM: --gres=gpu:A100:2  --mem=80G  --time=8:00:00
MODEL="Qwen/Qwen2.5-32B-Instruct"
python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL}" \
    --tensor-parallel-size 2 \
    --dtype bfloat16 \
    --port 8000 \
    --host 0.0.0.0 \
    --max-model-len 8192 \
    --trust-remote-code \
    --uvicorn-log-level warning

# ── Llama 3.3 70B ────────────────────────────────────────────────────────────
# SLURM: --gres=gpu:A100:4  --mem=160G  --time=12:00:00
MODEL="meta-llama/Llama-3.3-70B-Instruct"
python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL}" \
    --tensor-parallel-size 4 \
    --dtype bfloat16 \
    --port 8000 \
    --host 0.0.0.0 \
    --max-model-len 8192 \
    --trust-remote-code \
    --uvicorn-log-level warning
