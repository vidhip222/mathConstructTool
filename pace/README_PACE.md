# Running MathConstruct on PACE Phoenix (Georgia Tech HPC)

This guide explains how to reproduce MathConstruct results using **Llama 3.3 70B**
with **tool-calling** (Z3, OR-Tools, MiniZinc, SymPy, etc.) on PACE Phoenix.

---

## Architecture

```
PACE Login Node
    │
    ├─ [sbatch] GPU Node  ──────────────────────────────────────────────
    │       vLLM server (Llama 3.3 70B, port 8000)
    │       Tools: Z3, OR-Tools, MiniZinc, SymPy, CryptoMiniSat, NetworkX
    │
    └─ [sbatch] CPU Node  ──────────────────────────────────────────────
            MathConstruct benchmark client
            Sends problems → vLLM → gets tool-augmented answers → checks
```

---

## Step 0 — Prerequisites

### 0.1 Request a PACE account
- Go to https://pace.gatech.edu and request access to PACE Phoenix.
- Note your **account name** (used in `--account` SLURM directives).

### 0.2 Get HuggingFace access to Llama 3.3
- Go to https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct
- Accept Meta's license and request access.
- Create a HF token: https://huggingface.co/settings/tokens

---

## Step 1 — Clone the repo on PACE

```bash
# SSH into PACE
ssh <username>@login-phoenix.pace.gatech.edu

# Clone (or copy your local checkout)
git clone https://github.com/your-repo/mathconstruct.git
cd mathconstruct
```

---

## Step 2 — Set up the environment

```bash
# Run the setup script (only needed once)
chmod +x pace/setup_env.sh
./pace/setup_env.sh
```

This script:
- Creates a conda environment `mathconstruct` with Python 3.12
- Installs all Python dependencies via `uv`
- Installs solver packages: `z3-solver`, `ortools`, `pycryptosat`, `networkx`, `sympy`, `vllm`
- Downloads and installs **MiniZinc** binaries to `~/.local/minizinc/`
- Gives guidance on **GAP** and **Lean 4** (optional)

---

## Step 3 — Download the model weights

```bash
conda activate mathconstruct

# Login to HuggingFace
huggingface-cli login   # paste your HF token

# Download Llama 3.3 70B (about 140 GB, will be cached in ~/.cache/huggingface/)
huggingface-cli download meta-llama/Llama-3.3-70B-Instruct
```

> **Tip:** Download on a login node or use an interactive session.
> This can take 30–60 minutes depending on network speed.

---

## Step 4 — Edit the SLURM scripts

Open both scripts and replace `YOUR_PACE_ACCOUNT` with your actual account:

```bash
# In run_vllm_server.sh and run_benchmark.sh:
#SBATCH --account=YOUR_PACE_ACCOUNT   →   #SBATCH --account=gt-mylab123
```

Check that the **partition** names match what PACE gives you:
```bash
sinfo -s   # lists available partitions and their status
```

Common PACE partitions:
| Partition | GPU | Notes |
|---|---|---|
| `gpu-a100-40` | A100 40 GB | 2 GPUs = 80 GB, fits 70B in bf16 |
| `gpu-a100-80` | A100 80 GB | 1 GPU fits 70B |
| `gpu-v100` | V100 32 GB | Too small for 70B; use int8 |
| `cpu-medium` | — | For the benchmark client |

---

## Step 5 — Submit the jobs

```bash
mkdir -p logs

# 5a. Submit the vLLM server job and capture the job ID
VLLM_JOB_ID=$(sbatch --parsable pace/run_vllm_server.sh)
echo "vLLM server job ID: ${VLLM_JOB_ID}"

# 5b. Submit the benchmark — starts only after the server job begins running
sbatch --dependency=after:${VLLM_JOB_ID} pace/run_benchmark.sh
```

> `--dependency=after:ID` starts the benchmark job as soon as the server job
> moves from PENDING → RUNNING (not after it finishes).

---

## Step 6 — Monitor

```bash
# Watch job queue
watch -n 30 squeue -u $USER

# Tail vLLM server log
tail -f logs/vllm_<JOB_ID>.out

# Tail benchmark log
tail -f logs/benchmark_<JOB_ID>.out
```

---

## Step 7 — Analyze results

After the benchmark finishes, results are in `outputs/llama-tools-run/`.

```bash
conda activate mathconstruct

# Full analysis
uv run python src/scripts/analyze.py --run outputs/llama-tools-run

# Per-category breakdown
uv run python src/scripts/analyze.py --run outputs/llama-tools-run --only-info
```

---

## Memory guide for Llama 3.3 70B

| Precision | VRAM needed | SLURM config |
|---|---|---|
| `bfloat16` (default) | ~140 GB | `--gres=gpu:A100:2` (2×80GB) or `4×40GB` |
| `float8` / `fp8` | ~70 GB | `--gres=gpu:A100:1` (80GB) |
| `int4` (AWQ/GPTQ) | ~35 GB | `--gres=gpu:A100:1` (40GB) |

To use a quantized model, change `MODEL` in `run_vllm_server.sh`:
```bash
MODEL="hugging-quants/Meta-Llama-3.3-70B-Instruct-AWQ-INT4"
```
And remove `--dtype bfloat16` (quantized models ignore this).

---

## Tool availability on PACE

| Tool | How to use on PACE | Free? |
|---|---|---|
| Z3 | `pip install z3-solver` (done by setup_env.sh) | ✅ |
| OR-Tools | `pip install ortools` (done by setup_env.sh) | ✅ |
| MiniZinc | Downloaded by setup_env.sh to `~/.local/minizinc/` | ✅ |
| CryptoMiniSat | `pip install pycryptosat` | ✅ |
| NetworkX | `pip install networkx` | ✅ |
| SymPy | `pip install sympy` | ✅ |
| SageMath | `conda install -c conda-forge sage` (large, ~3 GB) | ✅ |
| GAP | `module load gap` or `conda install -c conda-forge gap-system` | ✅ |
| Lean 4 | `curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf \| sh` | ✅ |
| Wolfram Alpha | API key required, paid beyond free tier | ❌ |
| Mathematica | Commercial license required | ❌ |
| Maple | Commercial license required | ❌ |

---

## Troubleshooting

**vLLM OOM (out of memory)**
- Reduce `--max-model-len` in `run_vllm_server.sh`
- Use a quantized model (see Memory guide above)
- Request more GPUs

**Benchmark can't reach vLLM**
- Check that `logs/vllm_node.txt` was written
- PACE compute nodes may need InfiniBand/internal networking — the GPU and CPU nodes must be on the same fabric
- Try running both jobs on the same node type

**`minizinc: command not found`**
- Run `export PATH="${HOME}/.local/minizinc/bin:$PATH"` or add to `~/.bashrc`

**Tool returns `ToolNotFound`**
- The solver is not installed or not on PATH in the compute node environment
- Check that `conda activate mathconstruct` is in your job script
- The ToolSolver will fall back gracefully to Python for that problem

**Lean / GAP not available**
- These are optional; the solver skips them if not found
- Problems where Lean/GAP would be ideal will still be attempted with Python/SymPy/Z3
