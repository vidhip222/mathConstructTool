"""Tool registry for MathConstruct tool-calling solver."""
from .base_tool import BaseTool
from .python_tool import PythonTool
from .z3_tool import Z3Tool
from .ortools_tool import ORToolsTool
from .sympy_tool import SymPyTool
from .networkx_tool import NetworkXTool
from .cryptominisat_tool import CryptoMiniSatTool

from math_construct.problems.problem import Tag

# Category → ordered list of tool classes (most specialised first, Python always last as fallback)
_CATEGORY_TOOLS: dict = {
    Tag.NUMBER_THEORY:  [Z3Tool, SymPyTool, CryptoMiniSatTool, PythonTool],
    Tag.COMBINATORICS:  [ORToolsTool, Z3Tool, NetworkXTool, PythonTool],
    Tag.ALGEBRA:        [SymPyTool, Z3Tool, PythonTool],
    Tag.GEOMETRY:       [SymPyTool, PythonTool],
    Tag.PUZZLE:         [ORToolsTool, Z3Tool, PythonTool],
}

_DEFAULT_TOOLS = [PythonTool, Z3Tool, SymPyTool, ORToolsTool]


def get_tools_for_problem(problem, timeout: int = 30) -> list[BaseTool]:
    """Return the appropriate tools for a problem based on its category tags.

    Tools are deduplicated and ordered: most specialised first, Python last.
    If the problem has no recognised tags, returns the default set.
    """
    tags = getattr(problem.config, "tags", [])
    seen: set = set()
    result: list[BaseTool] = []

    for tag in tags:
        for cls in _CATEGORY_TOOLS.get(tag, []):
            if cls not in seen:
                seen.add(cls)
                result.append(cls(timeout=timeout))

    if not result:
        for cls in _DEFAULT_TOOLS:
            result.append(cls(timeout=timeout))

    return result
