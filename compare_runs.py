"""
Compare accuracy and error breakdown across 4 runs:
  llama8b-cot-run, llama8b-tool-run, qwen32b-cot-run, qwen32b-tool-run

Run from mathConstructTool/:
  uv run python compare_runs.py
"""

import sys
sys.path.insert(0, "src")

from src.scripts.analyze import analyze_run
from math_construct.problems import get_all_problem_classes
from math_construct.problems.problem import Tag

RUNS = [
    ("llama8b-cot-run",  "Llama-3.1-8B",  "CoT"),
    ("llama8b-tool-run", "Llama-3.1-8B",  "Tool"),
    ("qwen32b-cot-run",  "Qwen2.5-32B",   "CoT"),
    ("qwen32b-tool-run", "Qwen2.5-32B",   "Tool"),
]

ERROR_ORDER = [
    "CheckerTag.CORRECT",
    "CheckerTag.INCORRECT_SOLUTION",
    "CheckerTag.INCORRECT_FORMAT",
    "CheckerTag.INCORRECT_LENGTH",
    "No Boxed Answer",
    "Model says no solution exists",
    "Error parsing solution",
]

def get_tag_for_problem(problem_name, problem_classes):
    pc = problem_classes.get(problem_name)
    if pc is None:
        return "Unknown"
    tags = getattr(pc.config, "tags", [])
    # Return first Tag enum that is a category
    category_tags = [Tag.COMBINATORICS, Tag.NUMBER_THEORY, Tag.ALGEBRA, Tag.GEOMETRY, Tag.PUZZLE]
    for t in category_tags:
        if t in tags or t.value in tags or str(t) in tags:
            return t.name.replace("_", " ").title()
    return str(tags[0]) if tags else "Other"

def main():
    problem_classes = {pc.config.name: pc for pc in get_all_problem_classes()}

    all_results = []
    for run_dir, model_label, solver_label in RUNS:
        print(f"Analyzing {run_dir} ...", flush=True)
        _, model_results = analyze_run(f"outputs/{run_dir}", max_variations=2)
        # model_results has one key (the model folder name)
        for model_key, res in model_results.items():
            all_results.append({
                "run": run_dir,
                "model": model_label,
                "solver": solver_label,
                **res,
            })

    # ── Main summary table ─────────────────────────────────────────────────────
    col_w = [16, 6, 8, 10, 12, 9]
    header = f"{'Model':<{col_w[0]}} {'Solver':<{col_w[1]}} {'Avg Acc':>{col_w[2]}} {'All Correct':>{col_w[3]}} {'Problems':>{col_w[4]}} {'Cost $':>{col_w[5]}}"
    sep = "-" * sum(col_w + [len(col_w) - 1])
    print("\n" + "=" * len(sep))
    print("OVERALL ACCURACY")
    print("=" * len(sep))
    print(header)
    print(sep)
    for r in all_results:
        n_problems = len(r["detailed_results"]) // 2  # 2 variations each
        print(
            f"{r['model']:<{col_w[0]}} {r['solver']:<{col_w[1]}} "
            f"{r['avg_acc']*100:>{col_w[2]}.2f}% "
            f"{r['all_correct']*100:>{col_w[3]}.2f}%   "
            f"{n_problems:>{col_w[4]}}    "
            f"{r['avg_cost']:>{col_w[5]}.4f}"
        )

    # ── Tools vs CoT delta ─────────────────────────────────────────────────────
    print("\n" + "=" * len(sep))
    print("TOOL CALLING DELTA (Tool - CoT)")
    print("=" * len(sep))
    by_model = {}
    for r in all_results:
        by_model.setdefault(r["model"], {})[r["solver"]] = r
    for model, solvers in by_model.items():
        if "CoT" in solvers and "Tool" in solvers:
            delta_avg = (solvers["Tool"]["avg_acc"] - solvers["CoT"]["avg_acc"]) * 100
            delta_all = (solvers["Tool"]["all_correct"] - solvers["CoT"]["all_correct"]) * 100
            sign_avg = "+" if delta_avg >= 0 else ""
            sign_all = "+" if delta_all >= 0 else ""
            print(f"  {model:<18}  Avg Acc: {sign_avg}{delta_avg:.2f}%   All Correct: {sign_all}{delta_all:.2f}%")

    # ── Error breakdown table ──────────────────────────────────────────────────
    print("\n" + "=" * len(sep))
    print("ERROR TYPE BREAKDOWN (% of problems)")
    print("=" * len(sep))
    short_names = {
        "CheckerTag.CORRECT": "Correct",
        "CheckerTag.INCORRECT_SOLUTION": "Wrong Sol",
        "CheckerTag.INCORRECT_FORMAT": "Bad Format",
        "CheckerTag.INCORRECT_LENGTH": "Bad Length",
        "No Boxed Answer": "No Box",
        "Model says no solution exists": "Says None",
        "Error parsing solution": "Parse Err",
    }
    ew = 11
    err_header = f"{'Model':<16} {'Solver':<6} " + " ".join(f"{short_names[e]:>{ew}}" for e in ERROR_ORDER)
    print(err_header)
    print("-" * len(err_header))
    for r in all_results:
        et = r["error_types"]
        row = f"{r['model']:<16} {r['solver']:<6} "
        row += " ".join(f"{et.get(e, 0)*100:>{ew}.1f}%" for e in ERROR_ORDER)
        print(row)

    # ── Per-category accuracy ──────────────────────────────────────────────────
    print("\n" + "=" * len(sep))
    print("PER-CATEGORY ACCURACY (avg acc %)")
    print("=" * len(sep))

    categories = ["Number Theory", "Combinatorics", "Algebra", "Geometry", "Puzzle"]
    cat_header = f"{'Model':<16} {'Solver':<6} " + " ".join(f"{c[:8]:>9}" for c in categories)
    print(cat_header)
    print("-" * len(cat_header))

    for r in all_results:
        cat_correct = {c: [] for c in categories}
        for d in r["detailed_results"]:
            cat = get_tag_for_problem(d["problem_name"], problem_classes)
            if cat in cat_correct:
                cat_correct[cat].append(d["correct"])
        row = f"{r['model']:<16} {r['solver']:<6} "
        for c in categories:
            vals = cat_correct[c]
            if vals:
                row += f"{sum(vals)/len(vals)*100:>9.1f}%"
            else:
                row += f"{'N/A':>9} "
        print(row)

if __name__ == "__main__":
    main()
