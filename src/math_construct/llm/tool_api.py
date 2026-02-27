"""
ToolAPIQuery — extends APIQuery with OpenAI function-calling support.

Works with any OpenAI-compatible endpoint:
  - vLLM serving Llama 3.3 70B locally
  - Together AI
  - OpenRouter
  - Standard OpenAI

Usage:
    querier = ToolAPIQuery(
        model="meta-llama/Llama-3.3-70B-Instruct",
        api="openai",          # vLLM uses openai-compat API
        tools=[Z3Tool(), ORToolsTool()],
        tool_executor=...,     # callable: (tool_name, kwargs) -> str
        max_tool_rounds=5,
        ...
    )
"""
import json
from typing import Callable
from loguru import logger
from openai import OpenAI

from .api import APIQuery
from .tools.base_tool import BaseTool


class ToolAPIQuery(APIQuery):
    """
    Thin wrapper around APIQuery that adds tool / function-calling support.

    Extra constructor args
    ---------------------
    tools : list[BaseTool]
        Tool objects whose `.schema` will be sent to the LLM.
    tool_executor : Callable[[str, dict], str]
        Function that accepts (tool_name, kwargs) and returns the tool output string.
    max_tool_rounds : int
        Maximum number of tool-call / tool-result turns before we force a final answer.
    """

    def __init__(
        self,
        tools: list[BaseTool],
        tool_executor: Callable[[str, dict], str],
        max_tool_rounds: int = 5,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.tools = tools
        self.tool_executor = tool_executor
        self.max_tool_rounds = max_tool_rounds
        self._tool_schemas = [t.schema for t in tools]
        self._tool_map = {t.name: t for t in tools}

    # ------------------------------------------------------------------
    # Override run_query to support tool calling
    # ------------------------------------------------------------------

    def run_query(self, query: list[dict]) -> dict:
        """
        Execute a multi-turn tool-calling conversation.

        Keeps calling the LLM until:
          - It returns a normal assistant message (no tool_calls), OR
          - max_tool_rounds is reached (we then ask for a final answer).

        Returns the standard {output, input_tokens, output_tokens} dict
        where `output` is the final assistant text string.
        """
        messages = self._prepare_query_messages(query)
        total_input = 0
        total_output = 0
        final_text = ""

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=0,
        )

        for round_idx in range(self.max_tool_rounds + 1):
            # On the last round, remove tools to force a plain text answer
            tools_arg = self._tool_schemas if round_idx < self.max_tool_rounds else None

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                tools=tools_arg,
                tool_choice="auto" if tools_arg else None,
                **{k: v for k, v in self.kwargs.items()
                   if k not in ("tools", "tool_choice")},
            )

            total_input += response.usage.prompt_tokens
            total_output += response.usage.completion_tokens

            choice = response.choices[0]
            msg = choice.message

            # No tool calls — this is the final answer
            if not msg.tool_calls:
                final_text = msg.content or ""
                break

            # Append assistant message with tool_calls to the conversation
            messages.append(msg.model_dump(exclude_unset=False))

            # Execute each requested tool call
            for tc in msg.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_kwargs = json.loads(tc.function.arguments)
                except json.JSONDecodeError as e:
                    tool_output = f"ArgumentParseError: {e}"
                    logger.warning(f"Could not parse tool arguments for {tool_name}: {e}")
                else:
                    tool = self._tool_map.get(tool_name)
                    if tool is None:
                        tool_output = f"ToolNotFound: '{tool_name}' is not a registered tool."
                        logger.warning(tool_output)
                    else:
                        logger.debug(f"Executing tool '{tool_name}' with kwargs: {list(tool_kwargs.keys())}")
                        tool_output = self.tool_executor(tool_name, tool_kwargs)
                        logger.debug(f"Tool '{tool_name}' returned: {tool_output[:200]}")

                # Feed result back as a tool message
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(tool_output),
                })

            # After the last tool round, instruct the model to give its final answer
            if round_idx == self.max_tool_rounds - 1:
                messages.append({
                    "role": "user",
                    "content": (
                        "You have used all available tool calls. "
                        "Now write your final answer, encasing it in \\boxed{} as instructed."
                    ),
                })

        return {
            "output": final_text,
            "input_tokens": total_input,
            "output_tokens": total_output,
        }

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _prepare_query_messages(self, query: list[dict]) -> list[dict]:
        """Convert our internal message format to the OpenAI messages list."""
        messages = []
        for msg in query:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("system", "user", "assistant"):
                messages.append({"role": role, "content": content})
            # skip api_error and other internal roles
        return messages
