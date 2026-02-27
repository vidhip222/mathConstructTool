from math_construct.problems import get_problem_class, get_all_problem_classes
from math_construct.llm import APIQuery
import re
import os
from loguru import logger
import json

SYSTEM_PROMPT = r"""You are tasked to revise the problem statement given by the user to an equivalent one. Specifically, your generated alternative should be semantically equivalent to the original problem statement in every way. Pay specific attention to the following details:

1. The answer to the problem should remain the same. Under no circumstance should the answer change, or should any part of the problem be left out or added.
2. You should assume that all aspects of the problem are important and should be preserved in the revision.
3. The revised problem should be significantly rephrased, but should still contain the exact same principles and ideas as the original problem. Any background story or context should be kept intact.

In addition to the problem statement, you will also be given the formatting instructions. These instructions should also be revised to match the new problem statement, but should also maintain equivalence with the original formatting instructions.

Provide your answer using the following format:

### Reasoning ###
[[Here, you should provide a detailed explanation of how the problem can be rephrased while maintaining mathematical equivalence.]]

### Revised Problem ###
[[Here, you should provide the revised problem statement.]]

### Revised Formatting Instructions ###
[[Here, you should provide the revised formatting instructions.]]"""

def perform_number_check(original_problem, new_problem):
    # using re, extract the numbers from the original and new problems, then ensure they are the same
    original_numbers = re.findall(r'\d+', str(original_problem))
    new_numbers = re.findall(r'\d+', str(new_problem))
    # allow for a different order
    sorted_original = sorted([float(x) for x in original_numbers])
    sorted_new = sorted([float(x) for x in new_numbers])
    if len(sorted_original) != len(sorted_new):
        logger.warning(f"Number check failed: {sorted_original} vs {sorted_new}")
        return False
    for i in range(len(sorted_original)):
        if sorted_original[i] != sorted_new[i]:
            logger.warning(f"Number check failed: {sorted_original} vs {sorted_new}")
            return False
    return True

def format_problem(problem, formatting):
    return f"### Problem ###\n{problem}\n\n### Formatting Instructions ###\n{formatting}"

def extract_new_problem(result):
    return result.split("### Revised Problem ###")[1].split("### Revised Formatting Instructions ###")[0].strip()

def extract_new_formatting(result):
    return result.split("### Revised Formatting Instructions ###")[1].strip()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the LLM deduplication script")
    parser.add_argument("--model", type=str, default="openai:gpt-4o", help="The model to use")
    parser.add_argument("--output", type=str, default="data/revised_problems.json", help="The output file")
    parser.add_argument("--n-variations", type=int, default=4, help="Number of variations to generate for each problem")

    args = parser.parse_args()
    api, model = args.model.split(":")
    logger.info(f"Using model {model} with API {api} to run deduplication and saving results to {args.output}")
    all_problems = get_all_problem_classes()
    problem_instances = []
    for problem in all_problems:
        generated_variations = problem.generate_multiple(args.n_variations)
        for i, variation in enumerate(generated_variations):
            problem_instances.append({
                "problem": problem,
                "instance": variation,
                "variation": i
            })

    queries = []
    for problem_text in problem_instances:
        queries.append([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": format_problem(problem_text["instance"], problem_text["instance"].get_formatting())},
        ])
    querier = APIQuery(
        model=model,
        api=api,
        temperature=0.7,
        top_p=1.0,
        max_tokens=2048,
        concurrent_requests=10,
        timeout=60
    )

    results, _, cost = querier.run_queries(queries)
    logger.info(f'Cost is {cost["cost"]}')
    output_data = []

    for problem_instance, result in zip(problem_instances, results):
        try:
            new_problem = extract_new_problem(result)
            new_formatting = extract_new_formatting(result)
        except:
            logger.error(f"Failed to extract new problem and formatting for problem {problem_instance['problem'].config.name} and variation {problem_instance['variation']}. Model answer: {result}")
            new_problem = ""
            new_formatting = ""
        problem_instance["instance"].set_revision(new_problem, new_formatting)
        if not perform_number_check(problem_instance["instance"].get_problem(), str(problem_instance["instance"])):
            logger.warning(f"Number check failed for problem {problem_instance['problem'].config.name} and variation {problem_instance['variation']}. You should check this problem manually to ensure correctness.")
        output_data.append(problem_instance["instance"].to_json())

    # store to json
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=4)

    with open('src/scripts/latex/revised_problems.tex', 'w') as f:
        # print summary table of size per group 
        current_group = None
        current_problem = None
        for problem_dict in output_data:
            problem_name = problem_dict["config"]["name"]
            problem_class = get_problem_class(problem_name)
            revision = problem_class.from_json(problem_dict)
            group = revision.config.name.split("-")[0]
            if group != current_group:
                current_group = group
                f.write(f"\\section{{{group.replace('_', '-')}}}\n")
            if revision.config.name != current_problem:
                current_problem = revision.config.name
                f.write(f"\\subsection{{{revision.config.name}}}\n")

            f.write(f"\\subsubsection{{Variation}}\n")
            orig_problem = str(revision.get_problem())
            revised_problem = str(revision)
            old_formatting = revision.get_formatting_instructions()
            new_formatting = revision.get_formatting()
            f.write(f"\\textbf{{Actual Problem}}\\\\\n")
            f.write(f"{orig_problem}\n\n{old_formatting}\n\n")
            f.write(f"\\textbf{{Revised Problem}}\\\\\n")
            f.write(f"{revised_problem}\n\n{new_formatting}\n\n")
