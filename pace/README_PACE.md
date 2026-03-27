# Running MathConstruct on PACE Phoenix (Georgia Tech HPC)

Runs three models (Llama 3.1 8B, Qwen2.5 32B, Llama 3.3 70B) each with and
without tool-calling on the full benchmark.

---

## API Keys — what you need

| Key | Required? | Why |
|---|---|---|
| HuggingFace token | **Yes, for Llama models** | Llama 3.1 8B and Llama 3.3 70B are gated — you must accept Meta's license |
| HuggingFace token | No for Qwen | Qwen2.5 32B is open access |
| OpenAI API key | **No** | vLLM accepts a dummy value; no real key needed |

To get a HuggingFace token:
1. Go to https://huggingface.co/settings/tokens → create a Read token
2. Accept Meta's license at https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
3. Accept Meta's license at https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct

---

## Architecture

Each model runs as an independent group of jobs:

```
Login Node
  │
  ├─ [sbatch] GPU node — server_llama8b.sh   (1× A100 40GB)
  │     ├─ [sbatch] CPU node — run_cot_llama8b.sh   → outputs/llama8b-cot-run/
  │     └─ [sbatch] CPU node — run_tool_llama8b.sh  → outputs/llama8b-tool-run/
  │
  ├─ [sbatch] GPU node — server_qwen32b.sh   (2× A100 40GB)
  │     ├─ [sbatch] CPU node — run_cot_qwen32b.sh   → outputs/qwen32b-cot-run/
  │     └─ [sbatch] CPU node — run_tool_qwen32b.sh  → outputs/qwen32b-tool-run/
  │
  └─ [sbatch] GPU node — server_llama70b.sh  (4× A100 40GB)
        ├─ [sbatch] CPU node — run_cot_benchmark.sh  → outputs/llama-cot-run/
        └─ [sbatch] CPU node — run_tool_benchmark.sh → outputs/llama-tools-run/
```

All six model+solver combinations can be submitted at once.
Each server writes its hostname to a model-specific file so jobs don't interfere.

---

## Step 1 — Upload and unzip

```bash
# On PACE login node after uploading mathconstruct.zip:
unzip mathconstruct.zip
cd mathconstruct
```

---

## Step 2 — Set up the environment (run once)

```bash
chmod +x pace/setup_env.sh
./pace/setup_env.sh
```

Creates conda env `mathconstruct`, installs Python deps, solver packages
(z3, ortools, pycryptosat, networkx, sympy, vllm), and MiniZinc binaries.

---

## Step 3 — Download model weights

```bash
conda activate mathconstruct

# Login to HuggingFace (needed for Llama models only)
huggingface-cli login    # paste your HF Read token

# Llama 3.1 8B (~16 GB)
huggingface-cli download meta-llama/Llama-3.1-8B-Instruct

# Qwen2.5 32B (~65 GB) — no token needed
huggingface-cli download Qwen/Qwen2.5-32B-Instruct

# Llama 3.3 70B (~140 GB)
huggingface-cli download meta-llama/Llama-3.3-70B-Instruct
```

Run on a login node or interactive session. Can take 1–3 hours total.

---

## Step 4 — Replace YOUR_PACE_ACCOUNT in all scripts

```bash
# Check your account name:
pace-whoami

# Replace in all scripts at once (swap gt-mylab123 with your real account):
sed -i 's/YOUR_PACE_ACCOUNT/gt-mylab123/g' \
    pace/server_llama8b.sh \
    pace/server_qwen32b.sh \
    pace/server_llama70b.sh \
    pace/run_cot_llama8b.sh \
    pace/run_tool_llama8b.sh \
    pace/run_cot_qwen32b.sh \
    pace/run_tool_qwen32b.sh \
    pace/run_cot_benchmark.sh \
    pace/run_tool_benchmark.sh
```

---

## Step 5 — Submit all jobs

Run from the project root on the login node:

```bash
mkdir -p logs

# --- Llama 3.1 8B ---
JOB_8B=$(sbatch --parsable pace/server_llama8b.sh)
echo "Llama 8B server job: ${JOB_8B}"
sbatch --dependency=after:${JOB_8B} pace/run_cot_llama8b.sh
sbatch --dependency=after:${JOB_8B} pace/run_tool_llama8b.sh

# --- Qwen2.5 32B ---
JOB_32B=$(sbatch --parsable pace/server_qwen32b.sh)
echo "Qwen 32B server job: ${JOB_32B}"
sbatch --dependency=after:${JOB_32B} pace/run_cot_qwen32b.sh
sbatch --dependency=after:${JOB_32B} pace/run_tool_qwen32b.sh

# --- Llama 3.3 70B ---
JOB_70B=$(sbatch --parsable pace/server_llama70b.sh)
echo "Llama 70B server job: ${JOB_70B}"
sbatch --dependency=after:${JOB_70B} pace/run_cot_benchmark.sh
sbatch --dependency=after:${JOB_70B} pace/run_tool_benchmark.sh
```

This submits 9 jobs total (3 servers + 6 benchmarks).
Each benchmark pair (CoT + tool) for a model runs concurrently against its server.

---

## Step 6 — Monitor

```bash
# Watch all your jobs
watch -n 30 squeue -u $USER

# Check a specific log (replace JOB_ID with actual ID from squeue):
tail -f logs/cot_llama8b_<JOB_ID>.out
tail -f logs/tool_qwen32b_<JOB_ID>.out
tail -f logs/vllm_llama70b_<JOB_ID>.out
```

---

## Step 7 — Analyze results

```bash
conda activate mathconstruct

uv run python src/scripts/analyze.py --run outputs/llama8b-cot-run
uv run python src/scripts/analyze.py --run outputs/llama8b-tool-run

uv run python src/scripts/analyze.py --run outputs/qwen32b-cot-run
uv run python src/scripts/analyze.py --run outputs/qwen32b-tool-run

uv run python src/scripts/analyze.py --run outputs/llama-cot-run
uv run python src/scripts/analyze.py --run outputs/llama-tools-run
```

---

## GPU memory guide

| Model | Precision | VRAM | SLURM `--gres` |
|---|---|---|---|
| Llama 3.1 8B | bfloat16 | ~16 GB | `gpu:A100:1` (40 GB) |
| Qwen2.5 32B | bfloat16 | ~65 GB | `gpu:A100:2` (2×40 GB) |
| Llama 3.3 70B | bfloat16 | ~140 GB | `gpu:A100:4` (4×40 GB) |

---

## Troubleshooting

**vLLM OOM**
- Reduce `--max-model-len` in the server script
- For 70B: use a quantized model `hugging-quants/Meta-Llama-3.3-70B-Instruct-AWQ-INT4` and remove `--dtype bfloat16`

**Benchmark can't reach vLLM**
- Check that `logs/vllm_node_<model>.txt` was written
- GPU and CPU nodes must be on the same internal fabric on PACE

**`minizinc: command not found`**
- `export PATH="${HOME}/.local/minizinc/bin:$PATH"`

**HuggingFace 401 / access denied**
- Run `huggingface-cli login` again and make sure you've accepted the model's license on the HF website

**Tool returns `ToolNotFound`**
- Make sure `conda activate mathconstruct` ran in the job script
- ToolSolver falls back to Python automatically for that problem
