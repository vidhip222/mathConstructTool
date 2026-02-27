from math_construct.llm import CodeSolver, CoTSolver, APIQuery
import math
class EmptyAPIQuery:
    def __init__(self, output=r"\boxed{1,2,3}"):
        self.output = output

    def run_queries(self, queries):
        return [
            self.output for _ in queries
        ]


def test_docker_python():
    code_solver = CodeSolver(querier=EmptyAPIQuery())
    python_script = "def test():\n    return 1\nprint(test())"
    assert code_solver.run_in_docker(python_script).strip() == "1"
    python_timeout_script = f"import time\ndef test():\n    time.sleep({2 * code_solver.timeout})\n    return 1\nprint(test())"
    assert "TimeOutError" in code_solver.run_in_docker(python_timeout_script).strip()
    # allocate 2GB of memory should return memory error
    total_times = math.ceil(code_solver.memory / 0.75) + 1
    python_memory_script = f"a = [0]  * {total_times} * 10**8"
    assert "RuntimeError: Process returned code 137" in code_solver.run_in_docker(python_memory_script).strip()
    # get available CPU resources, should be 100% at most
    python_cpu_script = """def get_docker_cpus():
    # Path to cgroup CPU quota file
    with open("/sys/fs/cgroup/cpu.max") as f:
        quota, period = f.readline().strip().split()
        quota = int(quota)
        period = int(period)
        if quota == -1:
            return os.cpu_count()  # No limit set
        return quota / period  # Effective CPU count
# Get the number of CPUs available in the container
cpus = get_docker_cpus()
print(cpus)"""
    assert float(code_solver.run_in_docker(python_cpu_script).strip()) == code_solver.cpus
    # make sure network is disabled
    python_network_script = "import socket\nprint(socket.gethostbyname(socket.gethostname()))"
    assert "socket.gaierror" in code_solver.run_in_docker(python_network_script).strip()
    python_import_works = "import numpy, scipy, sympy\nprint('success')"
    assert code_solver.run_in_docker(python_import_works).strip() == "success"

def test_parse_code():
    code_solver = CodeSolver(querier=EmptyAPIQuery())
    text_with_script = "This is a text with a script\n```python\nprint(1)\n```"
    assert code_solver.parse_code(text_with_script).strip() == "print(1)"
    test_with_two_scripts = "This is a text with a script\n```python\nprint(1)\n```\nand another script\n```python\nprint(2)\n```"
    assert code_solver.parse_code(test_with_two_scripts).strip() == "print(1)\n\n\nprint(2)"
    test_with_no_script = "This is a text with no script"
    assert code_solver.parse_code(test_with_no_script) == None


def test_run_code_blocks():
    code_solver = CodeSolver(querier=EmptyAPIQuery())
    python_scripts = ["import time\ndef test():\n    time.sleep(2)\n    return 1\nprint(test())", "def test():\n    return 2\nprint(test())"]
    assert code_solver.run_code_blocks(python_scripts) == ["1\n", "2\n"]
    python_scripts = [f"def test():\n    return {k}\nprint(test())" for k in range(21)]
    assert code_solver.run_code_blocks(python_scripts) == [f"{k}\n" for k in range(21)]
    code_solver = CodeSolver(querier=EmptyAPIQuery(), n_parallel_code_executions=8)
    assert code_solver.run_code_blocks(python_scripts) == [f"{k}\n" for k in range(21)]
    assert code_solver.run_code_blocks(python_scripts[:7]) == [f"{k}\n" for k in range(7)]


def test_build_queries_code():
    code_solver = CodeSolver(querier=EmptyAPIQuery(), max_code_iterations=1)
    queries = [
        [{"role": "system", "content": "System prompt"}, {"role": "user", "content": "User prompt"}], 
        [{"role": "system", "content": "System prompt"}, {"role": "user", "content": "User prompt with code: ```python\nprint('Something Strange')\n```"}]
    ]
    output_obj, indices = code_solver.build_queries_code(queries, [{"code": 0, "feedback": 0}, {"code": 0, "feedback": 0}])
    assert indices == [1]
    assert len(output_obj) == 2
    assert len(output_obj[0]) == 2
    assert len(output_obj[1]) == 3
    assert output_obj[1][2]["role"] == "user"
    assert "Something Strange" in output_obj[1][2]["content"] 

    queries = [
        [{"role": "system", "content": "System prompt"}, {"role": "user", "content": "User prompt"}], 
        [{"role": "system", "content": "System prompt"}, {"role": "user", "content": "User prompt with code: ```python\nprint('Something Strange')\n```"}]
    ]
    output_obj, indices = code_solver.build_queries_code(queries, [{"code": 1, "feedback": 0}, {"code": 1, "feedback": 0}])
    assert len(indices) == 0
    assert len(output_obj[1]) == 2