from .cot_solver import CoTSolver
import subprocess
import uuid
import os
import re
from concurrent.futures import ProcessPoolExecutor, as_completed, wait
import multiprocessing as mp
from loguru import logger
import numpy as np
from tqdm import tqdm
import ast
import time, threading

class CodeSolver(CoTSolver):
    def __init__(self, 
                timeout: float = 5, 
                image_name: str = "constructmath-sandbox", 
                cpus: int = 1, 
                memory: int = 1,
                max_code_iterations: int = 2,
                n_parallel_code_executions: int = 2,
                code_feedback_prompt: str = "Code Output:\n```{feedback}```\n",
                last_code_iteration_warning: str = "This was the last time your code can be executed. From now on, you will not be able to execute code.",
                stop_at_timeout: bool = False,
                max_length_feedback: int = 4000,
                **kwargs):
        """
        Initializes the CodeSolver with the specified parameters.

        Args:
            timeout (float): The maximum time allowed for code execution in seconds. Default is 5.
            image_name (str): The name of the Docker image to use for the sandbox environment. Default is "mathconstruct-sandbox".
            cpus (int): The number of CPUs allocated for the sandbox environment. Default is 1.
            memory (int): The amount of memory (in GB) allocated for the sandbox environment. Default is 1.
            max_code_iterations (int): The maximum number of times the code can be executed. Default is 2.
            n_parallel_code_executions (int): The number of parallel code executions allowed. Default is 2.
            code_feedback_prompt (str): The template for the code feedback prompt. Must contain the placeholder {feedback}. Default is "Code Output:\n```{feedback}```\n".
            last_code_iteration_warning (str): The warning message displayed when the last code iteration is reached. Default is "This was the last time your code can be executed. From now on, you will not be able to execute code."
            **kwargs: Additional keyword arguments passed to the superclass initializer.

        Raises:
            AssertionError: If the code_feedback_prompt does not contain the placeholder {feedback}.
        """
        assert "{feedback}" in code_feedback_prompt, "code_feedback_prompt must contain the placeholder {feedback}"
        # assert that the docker image is available
        assert os.system(f"docker image inspect {image_name} > /dev/null 2>&1") == 0, f"Docker image {image_name} not found. Please build the image using the provided Dockerfile (see README.md)."
        super().__init__(stop_at_timeout=stop_at_timeout, **kwargs)
        self.timeout = timeout
        self.image_name = image_name
        self.cpus = cpus
        self.memory = memory
        self.max_code_iterations = max_code_iterations
        self.code_feedback_prompt = code_feedback_prompt
        self.n_parallel_code_executions = n_parallel_code_executions
        self.last_code_iteration_warning = last_code_iteration_warning
        self.stop_at_timeout = stop_at_timeout
        self.max_length_feedback = max_length_feedback

    def run_in_docker(self, code: str,) -> str:
        """
        Executes the provided Python code inside a Docker container with restricted resources and no network access.
        Args:
            code (str): The Python code to be executed inside the Docker container.
        Returns:
            str: The standard output from the executed code if it runs successfully.
             If the code execution exceeds the specified timeout, returns a timeout error message.
             If the code execution fails, returns the runtime error message.
        """
        logger.trace(f"Running code:\n{code}")
        container_name = f"code-sandbox-{uuid.uuid4().hex}"
        cmd = [
            "docker", "run",
            "--init", 
            "--rm",
            "--network=none",           # Disable networking
            "--read-only",
            "--name", container_name,
            f"--memory={self.memory}g",
            f"--cpus={self.cpus}",
            "-i",                       # Keep stdin open to pipe in code
            self.image_name,
            "python",
            "-u",
            "-c", "import sys; exec(sys.stdin.read())"
        ]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,   # so we can write code via stdin
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True                # treat I/O as text
        )

        def watchdog():
            time.sleep(self.timeout + 10)
            if process.poll() is None:  # Still running, forcibly kill
                subprocess.run(["docker", "kill", "--signal=SIGKILL", container_name], capture_output=True)
                subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
                process.kill()

        threading.Thread(target=watchdog, daemon=True).start()
        try:
            # Wait for the container to complete (or raise TimeoutExpired)
            stdout, stderr = process.communicate(input=code, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "kill", container_name], capture_output=True)
            subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
            process.kill()
            return f"TimeOutError: exceeded {self.timeout} seconds timeout."
        except Exception as e:
            subprocess.run(["docker", "kill", container_name], capture_output=True)
            subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
            process.kill()
            return f"RuntimeError: {e}"

        # After process completes normally:
        returncode = process.returncode
        if returncode != 0:
            if stderr == "":
                return f"RuntimeError: Process returned code {returncode}, exceeded memory or CPU limit."
            # Container returned an error
            return f"RuntimeError:\n{stderr.strip()}"

        return stdout
    
    def extract_imports_and_definitions(self, code_str: str) -> str:
        """
        Takes a Python code string and returns only the top-level
        imports, function definitions, and class definitions.
        """
        try:
            tree = ast.parse(code_str)
        except SyntaxError:
            # If there's a syntax error, return an empty string.
            return ""

        # Filter out only specific node types we want to keep
        filtered_body = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef)):
                filtered_body.append(node)

        # Build a new module from the filtered AST nodes
        new_module = ast.Module(body=filtered_body, type_ignores=[])
        
        # Convert AST back to code (Python 3.9+).
        extracted_code = ast.unparse(new_module)
        return extracted_code
    
    def parse_code(self, response: str) -> str:
        """
        Extracts the last Python code block from a given response string.

        Args:
            response (str): The input string containing the response with potential Python code blocks.

        Returns:
            str: The last Python code block found in the response. If no code block is found, returns None.
        """
        # find a python code block
        match = re.findall(r"```python\n(.*?)```", response, re.DOTALL)
        if match is None or len(match) == 0:
            return None
        return "\n\n".join(match)
    
    def get_executable_code(self, query, iteration):
        """
        Extracts executable code from the last response in the query if the iteration count is within the allowed limit.

        Args:
            query (list): A list of dictionaries containing the query responses.
            iteration (int): The current iteration count.

        Returns:
            str or None: The extracted code if available and within the iteration limit, otherwise None.
        """
        if iteration >= self.max_code_iterations or not self.is_valid_trace(query):
            return None
        last_response = query[-1]["content"]
        code = self.parse_code(last_response)
        if code is None:
            return None
        prefix = ""
        for previous_query in query[:-1]:
            if previous_query["role"] == "assistant":
                code_previous = self.parse_code(previous_query["content"])
                if code_previous is not None:
                    imports_and_definitions = self.extract_imports_and_definitions(code_previous)
                    if imports_and_definitions != "" and imports_and_definitions is not None:
                        prefix += imports_and_definitions + "\n"

        return prefix + code
    
    def run_code_blocks(self, code_blocks: list[str]):
        """
        Executes a list of code blocks in parallel using a ThreadPoolExecutor.

        Args:
            code_blocks (list[str]): A list of code blocks to be executed.

        Returns:
            list: A list of results from executing the code blocks, maintaining the original order.
        """
        logger.debug(f"Running {len(code_blocks)} code blocks in parallel")
        results = [None] * len(code_blocks)
        extra_wait = (len(code_blocks) / self.n_parallel_code_executions + 1) * self.timeout
        overall_timeout = extra_wait + 10
        with ProcessPoolExecutor(max_workers=self.n_parallel_code_executions, 
                                 mp_context=mp.get_context("spawn")) as executor:
            # Create a mapping of futures to their index in the original list
            future_to_index = {executor.submit(self.run_in_docker, code): i 
                               for i, code in enumerate(code_blocks)}

            # Wait for all futures up to the overall timeout.
            done, not_done = wait(future_to_index.keys(), timeout=overall_timeout)

            with tqdm(total=len(code_blocks), desc="Executing code blocks", unit="block") as pbar:
                # Process completed futures
                for future in done:
                    index = future_to_index[future]
                    try:
                        result = future.result()
                        if result is None:
                            result = "No output was generated by the code."
                    except Exception as e:
                        logger.error(f"Error executing code block at index {index}: {e}")
                        result = f"Error executing code block: {e}"
                    results[index] = result
                    pbar.update(1)

                # For any futures that did not complete within the overall timeout,
                # cancel them and mark their result as a timeout error.
                for future in not_done:
                    index = future_to_index[future]
                    results[index] = f"TimeOutError: Code execution did not complete within {self.timeout} seconds."
                    pbar.update(1)
                    future.cancel()
    
        logger.debug(f"Finished running code blocks")
        return results
    
    def build_queries_code(self, queries: list[dict[str]], iterations: list[dict[int]]):
        """
        Builds and executes code queries, providing feedback for each query.

        Args:
            queries (list[dict[str]]): A list of query dictionaries.
            iterations (list[dict[int]]): A list of iteration dictionaries containing code blocks.

        Returns:
            tuple: A tuple containing:
                - queries (list[dict[str]]): The updated list of query dictionaries with feedback.
                - not_none_code_blocks_indices (list[int]): Indices of code blocks that were not None.
        """
        logger.debug(f"Building code queries")
        code_blocks = [
            self.get_executable_code(query, iteration['code']) 
                    for (query, iteration) in zip(queries, iterations)
        ]
        not_none_code_blocks_indices = [i for i, c in enumerate(code_blocks) if c is not None]
        not_none_code_blocks = [c for c in code_blocks if c is not None]
        logger.debug(f"Executing {len(not_none_code_blocks)} code blocks out of {len(queries)} queries")
        # Execute code in parallel
        results = self.run_code_blocks(not_none_code_blocks)
        for i, result in zip(not_none_code_blocks_indices, results):
            if result is not None and len(result) > self.max_length_feedback:
                result = "..." + result[-self.max_length_feedback:]
            if result is None:
                feedback = "No output was generated by the code."
            else:
                feedback = self.code_feedback_prompt.format(feedback=result)
            if iterations[i]['code'] == self.max_code_iterations - 1:
                feedback += "\n\n" + self.last_code_iteration_warning
            queries[i].append({"role": "user", "content": feedback})
        return queries, not_none_code_blocks_indices
    
    def solve_code_round(self, queries: list[dict[str]], iterations: list[dict[int]]):
        """
        Solves a round of code queries by running them through a querier and appending the responses.

        Args:
            queries (list[dict[str]]): A list of query dictionaries.
            iterations (list[dict[int]]): A list of iteration dictionaries.

        Returns:
            list[dict[str]]: The updated list of query dictionaries with responses appended.

        """
        logger.info(f"Performing code round")
        queries, code_indices = self.build_queries_code(queries, iterations)

        if self.stop_at_timeout:
            code_indices = self.remove_timeouts(queries, code_indices)

        if len(code_indices) == 0:
            return queries
        queries_code_indices = [queries[i] for i in code_indices]
        responses, detailed_cost, cost = self.querier.run_queries(queries_code_indices)
        self.cost += cost["cost"]
        for i, response, detail in zip(code_indices, responses, detailed_cost):
            queries[i] = self.add_response(queries[i], response)
            self.detailed_cost[i]["cost"] += detail["cost"]
            self.detailed_cost[i]["input_tokens"] += detail["input_tokens"] 
            self.detailed_cost[i]["output_tokens"] += detail["output_tokens"]
        logger.info(f"Finished code round")
        return queries

    def solve(self, problems: list):
        """
        Solves a list of problems by iteratively generating and refining code and feedback.

        Args:
            problems (list): A list of problems to be solved.

        Returns:
            list: A list of queries representing the solutions to the problems.

        The method performs the following steps:
        1. Generates initial queries for the problems.
        2. Iteratively refines the queries through multiple rounds of code generation and feedback parsing.
        3. Tracks the number of iterations for code and feedback for each problem.
        4. Continues the process until the maximum number of feedback rounds and code iterations is reached.

        Note:
            - `self.max_feedback_rounds` and `self.max_code_iterations` determine the stopping criteria for the iterations.
            - The method `solve_code_round` is used to generate code for the queries.
            - The method `solve_parse_feedback_round` is used to parse feedback and refine the queries.
        """
        logger.info(f"Solving {len(problems)} problems")
        self.cost = 0
        self.detailed_cost = [
            {
                "cost": 0,
                "input_tokens": 0,
                "output_tokens": 0,
            } for _ in range(len(problems))
        ]
        queries = self.solve_initial_round(problems)
        iterations = [
            {"code": 0, "feedback": 0} for _ in range(len(problems))
        ]
        parsed_responses = [None for _ in range(len(problems))]
        checker = [problem.parse_and_check(q) for problem, q in zip(problems, queries)]
        logger.info(f"Solved instances after initial round: {np.mean([c[1] for c in checker]):.5f}")
        for it in range(self.max_feedback_rounds + self.max_code_iterations):
            logger.info(f"Starting iteration {it}")    
            for _ in range(self.max_code_iterations):
                current_lengths = [len(q) for q in queries]
                # do a code round
                queries = self.solve_code_round(queries, iterations)
                new_lengths = [len(q) for q in queries]
                for i, (cl, nl) in enumerate(zip(current_lengths, new_lengths)):
                    if nl > cl:
                        iterations[i]["code"] += 1
                checker = [problem.parse_and_check(q) for problem, q in zip(problems, queries)]
                logger.info(f"Solved instances after code round: {np.mean([c[1] for c in checker]):.5f}")
            # do a feedback round
            queries, parsed_responses = self.solve_parse_feedback_round(problems, queries, 
                                                                        parsed_responses, iterations)
            new_lengths = [len(q) for q in queries]
            for i, (cl, nl) in enumerate(zip(current_lengths, new_lengths)):
                if nl > cl:
                    iterations[i]["feedback"] += 1
            
            checker = [problem.parse_and_check(q) for problem, q in zip(problems, queries)]
            logger.info(f"Solved instances after feedback round: {np.mean([c[1] for c in checker]):.5f}")
        # log cost
        logger.info(f"Total cost for generating solutions: {self.cost}")
        return queries, self.detailed_cost