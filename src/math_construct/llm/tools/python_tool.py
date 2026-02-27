"""General-purpose Python execution tool."""
from .base_tool import BaseTool


class PythonTool(BaseTool):
    name = "run_python"
    description = (
        "Execute arbitrary Python code and return its stdout. "
        "Use this to compute, brute-force search, or verify a mathematical answer. "
        "Print your final answer to stdout."
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
                            "description": "Valid Python code to execute. Print the result to stdout.",
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def run(self, code: str) -> str:
        return self._run_python_code(code)
