"""
Parse smoke-test results and generate a PDF report.
Usage: uv run python src/scripts/make_report.py
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

# ── path setup ────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

from math_construct.problems import get_problem_class

# ── config ────────────────────────────────────────────────────────────────────
RUNS = {
    "CoT (no tools)": os.path.join(ROOT, "outputs", "smoke-cot"),
    "Tool (ReAct)":   os.path.join(ROOT, "outputs", "smoke-tool"),
}

MODEL_DISPLAY = {
    "Qwen__Qwen3-32B":                    "Qwen3-32B",
    "meta-llama__Llama-3.1-8B-Instruct":  "Llama-3.1-8B",
    "meta-llama__Llama-3.3-70B-Instruct": "Llama-3.3-70B",
}

PROBLEM_DISPLAY = {
    "bxmo-2011-1":          "BxMO 2011 P1\n(Number Theory)",
    "dutch-2010-4":         "Dutch MO 2010 P4\n(Mixed)",
    "imo-shortlist-2018-c1":"IMO SL 2018 C1\n(Combinatorics)",
}

# ── parse results ─────────────────────────────────────────────────────────────
def parse_file(json_path, problem_name):
    problem_class = get_problem_class(problem_name)
    if problem_class is None:
        return None, "unknown problem"
    with open(json_path) as f:
        entries = json.load(f)
    entry = entries[0]
    response = entry["response"]
    problem_inst = problem_class.from_json(entry["problem"])
    _, is_correct, details = problem_inst.parse_and_check(response)
    cost = entry.get("cost", {})
    return is_correct, details, cost

results = {}   # results[run_label][model_display][problem_display] = (is_correct, details)
costs   = {}   # costs[run_label][model_display] = total_cost

for run_label, run_dir in RUNS.items():
    results[run_label] = {}
    costs[run_label]   = {}
    if not os.path.isdir(run_dir):
        print(f"WARNING: {run_dir} not found, skipping.")
        continue
    for raw_model, model_disp in MODEL_DISPLAY.items():
        model_dir = os.path.join(run_dir, raw_model)
        if not os.path.isdir(model_dir):
            continue
        results[run_label][model_disp] = {}
        total_cost = 0.0
        for raw_prob, prob_disp in PROBLEM_DISPLAY.items():
            json_path = os.path.join(model_dir, f"{raw_prob}.json")
            if not os.path.isfile(json_path):
                results[run_label][model_disp][prob_disp] = (None, "missing")
                continue
            is_correct, details, cost = parse_file(json_path, raw_prob)
            results[run_label][model_disp][prob_disp] = (is_correct, details)
            if isinstance(cost, dict):
                total_cost += cost.get("cost", 0.0)
        costs[run_label][model_disp] = total_cost

# ── colours ───────────────────────────────────────────────────────────────────
C_CORRECT = "#4caf50"   # green
C_WRONG   = "#f44336"   # red
C_MISSING = "#9e9e9e"   # grey
C_HEADER  = "#1565c0"   # dark blue

def cell_color(val):
    if val is True:  return C_CORRECT
    if val is False: return C_WRONG
    return C_MISSING

def cell_text(val):
    if val is True:  return "✓"
    if val is False: return "✗"
    return "?"

# ── build PDF ─────────────────────────────────────────────────────────────────
pdf_path = os.path.join(ROOT, "outputs", "smoke_test_report.pdf")

models   = list(MODEL_DISPLAY.values())
problems = list(PROBLEM_DISPLAY.values())
run_labels = list(RUNS.keys())

with PdfPages(pdf_path) as pdf:

    # ── Page 1: title ─────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")
    ax.text(0.5, 0.7,  "MathConstruct Smoke Test Report",
            ha="center", va="center", fontsize=22, fontweight="bold", color=C_HEADER)
    ax.text(0.5, 0.5,  "3 Problems · 3 Models · CoT vs Tool Calling (ReAct)",
            ha="center", va="center", fontsize=14, color="#555555")
    ax.text(0.5, 0.32,
            "Problems: BxMO 2011 P1 (Number Theory)  ·  Dutch MO 2010 P4 (Mixed)  ·  IMO SL 2018 C1 (Combinatorics)\n"
            "Models: Qwen3-32B  ·  Llama-3.1-8B  ·  Llama-3.3-70B\n"
            "API: HuggingFace Inference Providers",
            ha="center", va="center", fontsize=11, color="#333333")
    correct_patch  = mpatches.Patch(color=C_CORRECT, label="Correct (✓)")
    wrong_patch    = mpatches.Patch(color=C_WRONG,   label="Incorrect (✗)")
    missing_patch  = mpatches.Patch(color=C_MISSING, label="Missing / Error (?)")
    ax.legend(handles=[correct_patch, wrong_patch, missing_patch],
              loc="lower center", ncol=3, fontsize=11, framealpha=0.3)
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # ── Page 2: result grids side by side ─────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Correctness by Model × Problem", fontsize=15, fontweight="bold", color=C_HEADER, y=1.02)

    for ax, run_label in zip(axes, run_labels):
        n_rows = len(models)
        n_cols = len(problems)

        ax.set_xlim(0, n_cols)
        ax.set_ylim(0, n_rows)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(run_label, fontsize=13, fontweight="bold", pad=10)

        # column headers
        for j, prob in enumerate(problems):
            ax.text(j + 0.5, n_rows + 0.15, prob, ha="center", va="bottom",
                    fontsize=8.5, fontweight="bold", color="#333333")

        # row headers + cells
        for i, model in enumerate(models):
            row = n_rows - 1 - i
            ax.text(-0.08, row + 0.5, model, ha="right", va="center",
                    fontsize=9, fontweight="bold")
            for j, prob in enumerate(problems):
                val = results.get(run_label, {}).get(model, {}).get(prob, (None,))[0]
                color = cell_color(val)
                text  = cell_text(val)
                rect = mpatches.FancyBboxPatch(
                    (j + 0.05, row + 0.05), 0.9, 0.9,
                    boxstyle="round,pad=0.05", linewidth=0,
                    facecolor=color, alpha=0.85)
                ax.add_patch(rect)
                ax.text(j + 0.5, row + 0.5, text, ha="center", va="center",
                        fontsize=18, color="white", fontweight="bold")

    plt.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # ── Page 3: accuracy summary bar chart ────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))

    x = range(len(models))
    width = 0.35
    colors_run = [C_HEADER, "#f57c00"]

    for k, run_label in enumerate(run_labels):
        accuracies = []
        for model in models:
            probs = results.get(run_label, {}).get(model, {})
            correct = sum(1 for v, _ in probs.values() if v is True)
            total   = len(problems)
            accuracies.append(correct / total * 100 if total else 0)
        offset = (k - 0.5) * width
        bars = ax.bar([xi + offset for xi in x], accuracies, width,
                      label=run_label, color=colors_run[k], alpha=0.85, zorder=3)
        for bar, acc in zip(bars, accuracies):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 1.5,
                    f"{acc:.0f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_xticks(list(x))
    ax.set_xticklabels(models, fontsize=11)
    ax.set_ylabel("Accuracy (%)", fontsize=12)
    ax.set_ylim(0, 115)
    ax.set_title("Accuracy per Model: CoT vs Tool Calling", fontsize=13,
                 fontweight="bold", color=C_HEADER)
    ax.legend(fontsize=11)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # ── Page 4: per-problem accuracy ─────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))

    x = range(len(problems))
    prob_labels = [p.replace("\n", " ") for p in problems]

    for k, run_label in enumerate(run_labels):
        accuracies = []
        for prob in problems:
            correct = sum(
                1 for model in models
                if results.get(run_label, {}).get(model, {}).get(prob, (None,))[0] is True
            )
            accuracies.append(correct / len(models) * 100)
        offset = (k - 0.5) * width
        bars = ax.bar([xi + offset for xi in x], accuracies, width,
                      label=run_label, color=colors_run[k], alpha=0.85, zorder=3)
        for bar, acc in zip(bars, accuracies):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 1.5,
                    f"{acc:.0f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_xticks(list(x))
    ax.set_xticklabels(prob_labels, fontsize=10)
    ax.set_ylabel("Accuracy (%)", fontsize=12)
    ax.set_ylim(0, 115)
    ax.set_title("Accuracy per Problem: CoT vs Tool Calling", fontsize=13,
                 fontweight="bold", color=C_HEADER)
    ax.legend(fontsize=11)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # ── Page 5: cost table ────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.axis("off")
    ax.set_title("Estimated API Cost (USD)", fontsize=13, fontweight="bold",
                 color=C_HEADER, pad=12)

    col_labels = ["Model"] + run_labels + ["Total"]
    table_data = []
    for model in models:
        row = [model]
        total = 0.0
        for run_label in run_labels:
            c = costs.get(run_label, {}).get(model, 0.0)
            row.append(f"${c:.4f}")
            total += c
        row.append(f"${total:.4f}")
        table_data.append(row)

    # totals row
    totals_row = ["TOTAL"]
    grand = 0.0
    for run_label in run_labels:
        s = sum(costs.get(run_label, {}).get(m, 0.0) for m in models)
        totals_row.append(f"${s:.4f}")
        grand += s
    totals_row.append(f"${grand:.4f}")
    table_data.append(totals_row)

    tbl = ax.table(cellText=table_data, colLabels=col_labels,
                   loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    tbl.scale(1.3, 1.8)

    # style header
    for j in range(len(col_labels)):
        tbl[0, j].set_facecolor(C_HEADER)
        tbl[0, j].set_text_props(color="white", fontweight="bold")
    # style totals row
    for j in range(len(col_labels)):
        tbl[len(table_data), j].set_facecolor("#e3f2fd")
        tbl[len(table_data), j].set_text_props(fontweight="bold")

    plt.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

print(f"\nReport saved to: {pdf_path}")
