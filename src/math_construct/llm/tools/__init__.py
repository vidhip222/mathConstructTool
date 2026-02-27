"""Tool registry for MathConstruct tool-calling solver."""
from .base_tool import BaseTool
from .python_tool import PythonTool
from .z3_tool import Z3Tool
from .ortools_tool import ORToolsTool
from .minizinc_tool import MiniZincTool
from .cryptominisat_tool import CryptoMiniSatTool
from .gap_tool import GAPTool
from .networkx_tool import NetworkXTool
from .sympy_tool import SymPyTool
from .sage_tool import SageTool
from .lean_tool import LeanTool

from math_construct.problems.problem import Tag

# Maps each problem category Tag to the ordered list of tools to offer.
# Tools are offered to the LLM in this order (most relevant first).
CATEGORY_TOOLS: dict[Tag, list[type[BaseTool]]] = {
    Tag.NUMBER_THEORY: [Z3Tool, CryptoMiniSatTool, SymPyTool, GAPTool, PythonTool],
    Tag.COMBINATORICS:  [ORToolsTool, MiniZincTool, Z3Tool, NetworkXTool, PythonTool],
    Tag.ALGEBRA:        [SymPyTool, SageTool, Z3Tool, PythonTool],
    Tag.GEOMETRY:       [SymPyTool, SageTool, PythonTool],
    Tag.PUZZLE:         [ORToolsTool, MiniZincTool, Z3Tool, PythonTool],
}

# Fallback: all tools
ALL_TOOLS: list[type[BaseTool]] = [
    Z3Tool, ORToolsTool, MiniZincTool, CryptoMiniSatTool,
    GAPTool, NetworkXTool, SymPyTool, SageTool, LeanTool, PythonTool,
]


def get_tools_for_problem(problem, timeout: int = 30) -> list[BaseTool]:
    """
    Return instantiated tool objects appropriate for this problem's tags.
    If multiple category tags match, the union of tool classes is returned
    (preserving priority order, no duplicates).
    """
    seen: set[type[BaseTool]] = set()
    tool_classes: list[type[BaseTool]] = []

    for tag in problem.config.tags:
        for cls in CATEGORY_TOOLS.get(tag, []):
            if cls not in seen:
                seen.add(cls)
                tool_classes.append(cls)

    # Always include LeanTool for formal verification
    if LeanTool not in seen:
        tool_classes.append(LeanTool)

    # Fallback to all tools if no category matched
    if not tool_classes:
        tool_classes = ALL_TOOLS

    return [cls(timeout=timeout) for cls in tool_classes]
