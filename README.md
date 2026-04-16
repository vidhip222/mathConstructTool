# MathConstruct

MathConstruct is a benchmarking framework for evaluating language models on constructive proofs. This README explains how to run models, analyze results, and reproduce findings from our paper.

The project uses uv for package management.

**Update September 2025:** We have performed additional verification on the problems in our benchmark. As a results, we removed 5 problems from the benchmark and made corrections to 5 verification functions.

## Installation

This project uses `uv` for package management. To install `uv`, run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If you prefer a plain Python virtual environment (`.venv`) + `pip`, you can do:
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running Language Models

You can run LLMs on benchmark problems using:
```bash
uv run python src/scripts/run.py <config-file>
```

Each run is configured by a file in `configs/`, as documented in `src/config/run_config.py`.

For example, to run `gpt-4o` on `imo-shortlist-2001-c6` and `tot-*` problems with 2 variations per problem:
```bash
uv run python src/scripts/run.py configs/example.yaml
```

Each run dumps raw model responses to a folder under `outputs/`. If you set `test_run: True` in the config the results are not saved anywhere, parse+check are done instantly, and debug info is printed to stdout.

### Model Names and API Keys
In the config file, a model name is always specified as `api:model_name` (e.g., `openai:gpt-4o`). To run models, set the following environment variables:
- OpenAI (`openai`): `OPENAI_API_KEY`
- Anthropic (`anthropic`): `ANTHROPIC_API_KEY`
- Together (`together`): `TOGETHER_API_KEY`
- Google (`google`): `GOOGLE_API_KEY`
- Deepseek (`deepseek`): `DEEPSEEK_API_KEY`
- Openrouter (`openrouter`): `OPENROUTER_API_KEY`

### Tool mode parallelization and large-model behavior
To keep MathConstruct changes minimal while improving throughput, we only parallelize one specific step in tool mode:

- **Parallelized:** `ToolSolver.solve_initial_round` runs different **problems** concurrently (thread pool size = `inference.concurrent_requests`).
- **Not parallelized:** the internal tool loop for a **single problem** is still sequential (LLM call → tool call → LLM call ...).
- **No change to CoT/code solvers:** this affects only `solver.type_solver: tool` with native tool calling.

This means you can speed up large benchmark sweeps without changing the per-problem reasoning flow used in the original framework.

For OpenAI responses-oriented model families (e.g. `gpt-5`, `o1`, `o3`), the runner automatically uses ReAct tool mode in tool runs, because those models are not reliable with the native chat function-calling path used by `ToolAPIQuery`.

## Full benchmark against a locally hosted vLLM server

This is the recommended flow if you want to benchmark open-weight models (Qwen/Llama) on your own GPUs while using MathConstruct's existing configs.

### 1) Start vLLM (OpenAI-compatible endpoint)

Choose one model and launch a server on port 8000:

```bash
# Llama 3.1 8B
vllm serve meta-llama/Llama-3.1-8B-Instruct --port 8000 --tensor-parallel-size 1

# Qwen2.5 32B
vllm serve Qwen/Qwen2.5-32B-Instruct --port 8000 --tensor-parallel-size 2

# Llama 3.3 70B
vllm serve meta-llama/Llama-3.3-70B-Instruct --port 8000 --tensor-parallel-size 4
```

If you want **native function-calling** (`use_react: False`), start vLLM with tool-call flags:

```bash
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.3-70B-Instruct \
  --tensor-parallel-size 4 \
  --dtype bfloat16 \
  --port 8000 \
  --host 0.0.0.0 \
  --max-model-len 8192 \
  --enable-auto-tool-choice \
  --tool-call-parser llama3_json
```

For **ReAct tool mode** (`use_react: True`), those extra tool-call flags are not required.

### 2) Point MathConstruct to local vLLM

In config, set:
- `models: ["openai:<model-name>"]`
- `solver.local_api_base_url: "http://localhost:8000/v1"`

Also export a dummy key (required by OpenAI client init):

```bash
export OPENAI_API_KEY="dummy-local"
```

### 3) Run the full benchmark configs (all problems)

The PACE configs already target the **full benchmark** (`problems: [".*"]`) with 2 variations.

```bash
# Qwen2.5 32B
uv run python src/scripts/run.py configs/pace_qwen32b_cot.yaml
uv run python src/scripts/run.py configs/pace_qwen32b_tool.yaml

# Llama 3.1 8B
uv run python src/scripts/run.py configs/pace_llama8b_cot.yaml
uv run python src/scripts/run.py configs/pace_llama8b_tool.yaml

# Llama 3.3 70B
uv run python src/scripts/run.py configs/pace_llama_cot.yaml
uv run python src/scripts/run.py configs/pace_llama_tools.yaml
```

Each run writes to `outputs/<output_dir>/` (for example `outputs/qwen32b-tool-run`).

### 4) Analyze benchmark outputs

```bash
uv run python src/scripts/analyze.py --run outputs/qwen32b-cot-run
uv run python src/scripts/analyze.py --run outputs/qwen32b-tool-run
uv run python src/scripts/analyze.py --run outputs/llama8b-cot-run
uv run python src/scripts/analyze.py --run outputs/llama8b-tool-run
uv run python src/scripts/analyze.py --run outputs/llama-cot-run
uv run python src/scripts/analyze.py --run outputs/llama-tools-run
```

### Notes
- For local multi-GPU setups, tune `--tensor-parallel-size` and `inference.concurrent_requests` conservatively first.
- If you see OOMs, reduce `--max-model-len` and/or batch size in solver config.
- For full HPC orchestration (separate server + benchmark jobs), see `pace/README_PACE.md`.


## Processing the results of a run 

To analyze responses from a run:
```bash
uv run python src/scripts/analyze.py --run logs/example-run --only-info
```
This command loads responses, checks them, and reports metrics. Use `--problems` and `--models` to analyze subsets of a run.

## Inspecting data

To inspect results in the browser:
```bash
uv run python src/app/app.py --run logs/example-run
```
Open `http://localhost:5001/` in a browser, then click "[Reload all Data]" to view results. Use `--problems` and `--models` to analyze a subset of a run.

## Adding New Problems

All problems are defined in `src/math_objects/problems/`. To add a problem, create a class that inherits from `Problem` and define the following:

### Configuration

Problem config is a snippet of code that defines the problem with its statement, parameters that are inserted into the statement, formatting instructions for the output and problem source. We also include the original parameters and solution for the problem.

```python
config = ProblemConfig(
    name=Problem.get_name(__file__),
    statement=PROBLEM_TEMPLATE,
    formatting_instructions=FORMATTING_INSTRUCTIONS,
    parameters=["k"],
    source="IMO 2010 Shortlist N1",
    problem_url="https://www.imo-official.org/problems/IMO2010SL.pdf",
    solution_url="https://www.imo-official.org/problems/IMO2010SL.pdf",
    original_parameters={"k": 42},
    original_solution=get_solution(42),
    tags=[TAG.NUMBER_THEORY]
)
```

### Tags 
Tags describe the category (e.g., number theory), type (e.g., "Find any"), hardness compared to the original (e.g., "Simplified"), and other misc aspects (e.g., "Is translated"). For an explanation of tags, see the enum definition in `problem.py`. 

## Check method

Implement a `check` method to verify solutions:
```python
def check(self, x: list[list[int]]) -> Union[bool, tuple[bool, str, CheckerTag]]:
    ... # Implement the check
```
The checker returns a boolean (`True` if solution is correct), and ideally (but not required) a string with a reason why the solution is incorrect, and a CheckerTag categorizing that reason. Implement your function very defensively, and check for uniqueness of individual solutions, correct lengths, min and max allowed values, ...

### Generate method

Use `generate` to create a new problem instance:
```python
@staticmethod
def generate() -> "Problem2010N1":
    k = random.choice([42, 51])
    return Problem2010N1(k)
```

### Get Problem Statement method

Retrieve the formatted problem statement:
```python
def get_problem(self) -> str:
    return PROBLEM_TEMPLATE.format(k=self.k)
```

### Get Solution method

The `get_solution` method returns a correct solution to the given problem. It is displayed in the app and can also be used for testing.
```python
def get_solution(self) -> Any:
    return get_solution(self.k)
```

## Testing

Run all tests with:
```bash
uv run pytest src/tests
```
For specific problem tests:
```bash
uv run pytest src/tests/test_problems.py -k "problem23"
```

## Python-Augmented Reasoning
LLMs can use Python tool support in a sandboxed Docker environment. To enable:
```bash
docker build -t mathconstruct-sandbox docker/
```
Ensure Docker runs in rootless mode. You can enable Python-Augmented Reasoning in the config file.

## Reproducing results
Raw results are stored in `logs/`. Analyze results with:
```bash
uv run python src/scripts/analyze.py --run logs/example-run
```

### Logs for Specific Figures and Tables:
Specifically, the following folders correspond to the data in our paper:
- `cot-parser-main`: Table 2, Figure 5
- `code-parser-main`: Figure 4
- `code-brute-force`: First two columns of Table 3
- `code-brute-force-infer`: Last two columns of Table 3
- `cot-rephrase`: Figure 6
- `lengthstudy`: Figure 7

To regenerate plots, use `notebooks/plot.ipynb` with `matplotlib`, `numpy`, `seaborn`, and `pandas`.

### Full Reproduction
To reproduce results from scratch, set API keys and run:
```bash
bash run.sh
```
**Note:** This process may take several days and cost approximately $1000 USD.
