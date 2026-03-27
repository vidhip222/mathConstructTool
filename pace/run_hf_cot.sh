#!/usr/bin/env bash
# =============================================================================
# pace/run_hf_cot.sh — SLURM job: MathConstruct CoT via HuggingFace API
# =============================================================================
# No GPU node needed — all inference is remote via HuggingFace router.
#
# Before submitting, set your HF token:
#   export HF_TOKEN=hf_xxxxxxxxxxxx
#   sbatch --export=ALL pace/run_hf_cot.sh
#
# Or hardcode it below (line marked with <--).
# Adjust --account to match your PACE allocation.
# =============================================================================

#SBATCH --job-name=mc-hf-cot
#SBATCH --partition=cpu-medium
#SBATCH --account=YOUR_PACE_ACCOUNT       # <-- replace with your PACE account
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=48:00:00
#SBATCH --output=logs/hf_cot_%j.out
#SBATCH --error=logs/hf_cot_%j.err

set -euo pipefail

mkdir -p logs outputs

module purge
module load anaconda3/2023.09

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate mathconstruct

export PATH="${HOME}/.local/minizinc/bin:$PATH"

# HuggingFace token — passed via --export=ALL or set here:
# export HF_TOKEN="hf_xxxxxxxxxxxx"   # <-- uncomment and paste token if not exporting

if [[ -z "${HF_TOKEN:-}" ]]; then
    echo "ERROR: HF_TOKEN is not set. Export it before submitting:"
    echo "  export HF_TOKEN=hf_xxxxxxxxxxxx"
    echo "  sbatch --export=ALL pace/run_hf_cot.sh"
    exit 1
fi

echo "Starting HuggingFace CoT benchmark (all 3 models) ..."
uv run python src/scripts/run.py configs/pace_hf_cot.yaml

echo "Done. Results in outputs/hf-cot-run/"
