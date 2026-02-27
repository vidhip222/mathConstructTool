"""
Base tool abstraction for MathConstruct tool-calling solver.

Each tool:
  - Has a name and JSON schema (for OpenAI function-calling)
  - Runs code in a subprocess with a timeout
  - Returns stdout or a structured error string
"""
import subprocess
import tempfile
import os
import textwrap
from abc import ABC, abstractmethod
from loguru import logger


DEFAULT_TIMEOUT = 30  # seconds


class BaseTool(ABC):
    """Abstract base for all math solver tools."""

    name: str
    description: str

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Subclasses implement these two methods
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def schema(self) -> dict:
        """
        Return an OpenAI-compatible function schema, e.g.:
        {
            "type": "function",
            "function": {
                "name": "run_z3",
                "description": "...",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Python/Z3 code to run"}
                    },
                    "required": ["code"]
                }
            }
        }
        """
        ...

    @abstractmethod
    def run(self, **kwargs) -> str:
        """Execute the tool with the given arguments and return a result string."""
        ...

    # ------------------------------------------------------------------
    # Shared helper: run a Python code string in a subprocess
    # ------------------------------------------------------------------

    def _run_python_code(self, code: str, extra_env: dict | None = None) -> str:
        """
        Write `code` to a temp file and execute it with `python`.
        Returns stdout on success, or an error string on failure/timeout.
        """
        env = os.environ.copy()
        if extra_env:
            env.update(extra_env)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            proc = subprocess.run(
                ["python", tmp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env,
            )
            if proc.returncode != 0:
                stderr = proc.stderr.strip()
                return f"RuntimeError:\n{stderr}" if stderr else f"Process exited with code {proc.returncode}"
            return proc.stdout
        except subprocess.TimeoutExpired:
            return f"TimeoutError: execution exceeded {self.timeout}s"
        except Exception as e:
            return f"RuntimeError: {e}"
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _run_shell_command(self, cmd: list[str], stdin: str | None = None) -> str:
        """Run an arbitrary shell command, optionally passing stdin."""
        try:
            proc = subprocess.run(
                cmd,
                input=stdin,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            out = proc.stdout.strip()
            err = proc.stderr.strip()
            if proc.returncode != 0:
                return f"RuntimeError:\n{err}" if err else f"Process exited with code {proc.returncode}"
            return out if out else err
        except subprocess.TimeoutExpired:
            return f"TimeoutError: execution exceeded {self.timeout}s"
        except FileNotFoundError:
            return f"ToolNotFound: '{cmd[0]}' is not installed or not on PATH"
        except Exception as e:
            return f"RuntimeError: {e}"
