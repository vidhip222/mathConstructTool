"""NetworkX graph theory tool.

The LLM writes Python code that uses NetworkX to model and solve graph problems.

Install: pip install networkx
"""
from .base_tool import BaseTool

_PREAMBLE = "import networkx as nx\n"


class NetworkXTool(BaseTool):
    name = "run_networkx"
    description = (
        "Execute Python code that uses the NetworkX graph library. "
        "Use this for graph theory problems: coloring, matching, paths, flows, "
        "cliques, isomorphism, and combinatorics on graphs. "
        "Import with: import networkx as nx. Print your final answer to stdout."
    )

    @property
    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": (
                                "Python code using networkx. "
                                "Example: import networkx as nx; G = nx.petersen_graph(); "
                                "print(nx.chromatic_number(G))"
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def run(self, code: str) -> str:
        if "import networkx" not in code:
            code = _PREAMBLE + code
        return self._run_python_code(code)
