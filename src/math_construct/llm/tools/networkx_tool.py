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
        "Best for: graph colouring (chromatic number, chromatic polynomial), "
        "matchings (maximum matching, perfect matching), connectivity, "
        "independent sets, cliques, Hamiltonian paths, shortest paths, "
        "graph isomorphism, tree structures, and constructing graphs "
        "with prescribed degree sequences or adjacency properties. "
        "Import with: import networkx as nx. Print all results with print()."
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
                                "Python code using networkx (import networkx as nx). "
                                "Useful functions: nx.graph_coloring(), nx.max_weight_matching(), "
                                "nx.maximum_independent_set(), nx.find_cliques(), "
                                "nx.is_connected(), nx.shortest_path(). "
                                "Use print() for all output. "
                                "Example — find chromatic number and a proper colouring of a cycle C7:\n"
                                "  import networkx as nx\n"
                                "  G = nx.cycle_graph(7)\n"
                                "  colouring = nx.coloring.greedy_color(G, strategy='largest_first')\n"
                                "  num_colours = max(colouring.values()) + 1\n"
                                "  print('chromatic number:', num_colours)\n"
                                "  print('colouring:', colouring)"
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

    def react_prompt_block(self) -> str:
        return """\
### Tool: run_networkx
Best for: graph colouring, matchings, cliques, independent sets, connectivity,
          Hamiltonian paths, trees, and constructing graphs with given properties.
Action label: run_networkx
Parameter:
  code (string) — Python using networkx (import networkx as nx). Use print() for output.
Output: stdout from your code, or RuntimeError.

Example:
```python
import networkx as nx
# Build the Petersen graph and find its chromatic number
G = nx.petersen_graph()
colouring = nx.coloring.greedy_color(G, strategy='largest_first')
print("chromatic number >=", max(colouring.values()) + 1)
print("colouring:", colouring)
```
"""
