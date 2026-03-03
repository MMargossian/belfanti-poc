"""
Core agentic loop for the Belfanti CNC Manufacturing POC.

The :class:`Orchestrator` manages the conversation with Claude, dispatches
tool calls to the :class:`ToolExecutor`, and handles the approval-gate
pause/resume flow required by human-in-the-loop manufacturing workflows.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Generator

import anthropic

from agent.system_prompt import build_system_prompt
from agent.tool_executor import ToolExecutor
from state.store import get_state, set_state

logger = logging.getLogger(__name__)

# Type alias for the events yielded to the Streamlit UI layer.
# Each event is a tuple of (event_type, *payload).
AgentEvent = tuple[str, Any] | tuple[str, Any, Any]


class Orchestrator:
    """Drives the Claude agentic loop, dispatching tool calls and pausing at gates."""

    MODEL = "claude-sonnet-4-6"
    MAX_TOKENS = 4096
    MAX_ITERATIONS = 50  # safety cap to prevent runaway loops

    def __init__(self, api_key: str) -> None:
        self.client = anthropic.Anthropic(api_key=api_key)
        self.tool_executor = ToolExecutor()

    # ── Public API ────────────────────────────────────────────────────────

    def get_all_tools(self) -> list[dict]:
        """Collect tool definitions from all currently enabled modules."""
        enabled: list[str] = get_state("enabled_modules", [])
        return self.tool_executor.get_tools_for_modules(enabled)

    def run(self, user_message: str) -> Generator[AgentEvent, None, None]:
        """Main agentic loop. Called when the user sends a message.

        This is a **generator** that yields events for the Streamlit UI:

        * ``("text", content)`` -- assistant text to display
        * ``("tool_call", tool_name, tool_input)`` -- a tool is being invoked
        * ``("tool_result", tool_name, result_str)`` -- the tool's return value
        * ``("approval_needed", gate_name, gate_data)`` -- pause for human review
        * ``("done", None)`` -- the loop finished normally
        * ``("error", error_msg)`` -- an error occurred
        """
        # Append the user message to the conversation history.
        messages: list[dict] = get_state("agent_messages", [])
        messages.append({"role": "user", "content": user_message})
        set_state("agent_messages", messages)
        set_state("agent_running", True)

        try:
            yield from self._loop()
        except anthropic.APIConnectionError as exc:
            yield ("error", f"Could not reach the Anthropic API: {exc}")
        except anthropic.AuthenticationError:
            yield ("error", "Invalid API key. Please check your Anthropic API key in the sidebar.")
        except anthropic.RateLimitError:
            yield ("error", "Rate limit exceeded. Please wait a moment and try again.")
        except anthropic.APIStatusError as exc:
            yield ("error", f"Anthropic API error (status {exc.status_code}): {exc.message}")
        except Exception as exc:
            logger.exception("Unexpected error in orchestrator loop")
            yield ("error", f"Agent error: {exc}")
        finally:
            set_state("agent_running", False)

    def resume_after_approval(
        self,
        approval_result: str,
        feedback: str = "",
    ) -> Generator[AgentEvent, None, None]:
        """Resume the agentic loop after an approval gate.

        Parameters
        ----------
        approval_result:
            One of ``"approved"``, ``"rejected"``, or ``"changes_requested"``.
        feedback:
            Optional human feedback (required for rejection / change requests).
        """
        gate = get_state("approval_pending")
        set_state("approval_pending", None)
        set_state("approval_result", approval_result)

        if approval_result == "approved":
            message = (
                f"[APPROVAL GATE: {gate}] Result: APPROVED. "
                "Please proceed with the next steps."
            )
        elif approval_result == "rejected":
            message = (
                f"[APPROVAL GATE: {gate}] Result: REJECTED. {feedback}. "
                "Please stop the current process and explain what happens next."
            )
        else:
            message = (
                f"[APPROVAL GATE: {gate}] Result: CHANGES REQUESTED. "
                f"Feedback: {feedback}. Please revise accordingly."
            )

        yield from self.run(message)

    # ── Internal loop ─────────────────────────────────────────────────────

    def _loop(self) -> Generator[AgentEvent, None, None]:
        """Execute the iterative tool-use loop until Claude stops or a gate fires."""
        for iteration in range(1, self.MAX_ITERATIONS + 1):
            # 1. Build the system prompt from current state.
            pipeline_state = get_state("pipeline_state")
            enabled_modules: list[str] = get_state("enabled_modules", [])
            system_prompt = build_system_prompt(enabled_modules, pipeline_state)

            # 2. Gather available tools (may be empty if nothing is enabled).
            tools = self.get_all_tools()

            # 3. Call the Claude API.
            messages: list[dict] = get_state("agent_messages", [])

            api_kwargs: dict[str, Any] = {
                "model": self.MODEL,
                "max_tokens": self.MAX_TOKENS,
                "system": system_prompt,
                "messages": messages,
            }
            # Only include tools if we have any -- the API rejects an empty list.
            if tools:
                api_kwargs["tools"] = tools

            response = self.client.messages.create(**api_kwargs)

            # 4. Process response content blocks.
            assistant_content = response.content
            tool_use_blocks = []

            for block in assistant_content:
                if block.type == "text":
                    yield ("text", block.text)
                elif block.type == "tool_use":
                    tool_use_blocks.append(block)

            # 5. Serialize and persist the assistant turn.
            serialized_content = _serialize_content_blocks(assistant_content)
            messages.append({"role": "assistant", "content": serialized_content})
            set_state("agent_messages", messages)

            # 6. If there are no tool calls, the turn is complete.
            if response.stop_reason == "end_turn" or not tool_use_blocks:
                yield ("done", None)
                return

            # 7. Execute every tool call and collect results.
            tool_results: list[dict] = []
            for tool_block in tool_use_blocks:
                tool_name = tool_block.name
                tool_input = tool_block.input

                yield ("tool_call", tool_name, tool_input)

                result, result_str = _execute_tool_safe(
                    self.tool_executor, tool_name, tool_input
                )

                yield ("tool_result", tool_name, result_str)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result_str,
                })

                # 8. Check for approval gates.
                if isinstance(result, dict) and result.get("status") == "pending_approval":
                    gate_name = result.get("gate", "unknown")
                    set_state("approval_pending", gate_name)

                    # Persist tool results collected so far.
                    messages.append({"role": "user", "content": tool_results})
                    set_state("agent_messages", messages)

                    yield ("approval_needed", gate_name, result)
                    # Pause -- the UI will call resume_after_approval() later.
                    return

            # 9. Persist all tool results and loop back for the next iteration.
            messages.append({"role": "user", "content": tool_results})
            set_state("agent_messages", messages)

        # If we exhaust the iteration budget, report it.
        yield (
            "error",
            f"Maximum iterations ({self.MAX_ITERATIONS}) reached. "
            "The agent loop has been stopped as a safety measure.",
        )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _serialize_content_blocks(blocks) -> list[dict]:
    """Convert SDK content blocks to plain dicts suitable for the messages API."""
    serialized: list[dict] = []
    for block in blocks:
        if block.type == "text":
            serialized.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            serialized.append({
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input,
            })
    return serialized


def _execute_tool_safe(
    executor: ToolExecutor,
    tool_name: str,
    tool_input: dict,
) -> tuple[Any, str]:
    """Execute a tool call, catching exceptions and returning a JSON string.

    Returns
    -------
    (raw_result, json_string)
        The raw result (dict, list, str, etc.) and its JSON-serialised form.
        On error the raw result is an ``{"error": ...}`` dict.
    """
    try:
        result = executor.execute(tool_name, tool_input)
        if isinstance(result, str):
            result_str = result
        else:
            result_str = json.dumps(result, default=str)
    except Exception as exc:
        logger.exception("Tool execution failed: %s", tool_name)
        result = {"error": str(exc)}
        result_str = json.dumps(result)
    return result, result_str
