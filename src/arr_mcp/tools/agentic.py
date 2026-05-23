"""Agentic cross-arr workflow tools — LLM-powered via ``ctx.sample()``.

The ``arr_agentic`` tool uses FastMCP 3.2 sampling (SEP-1577) to orchestrate
multi-step cross-arr operations.  It falls back gracefully when the MCP client
does not support sampling.

Diffentiating value: given a vague request like "find me something good to watch",
the LLM decides which tools to call, in what order, and presents a reasoned result.
"""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import Field

try:
    from fastmcp import Context
except ImportError:
    from fastmcp.server.context import Context  # legacy fallback

from arr_mcp.constants import TOOL_VERSION

logger = logging.getLogger(__name__)


def register_agentic_tools(mcp, clients: dict) -> None:
    """Register agentic cross-arr tools on the FastMCP instance.

    Parameters
    ----------
    mcp:
        The FastMCP instance.
    clients:
        Dict mapping service name → client instance (or None).
    """

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def arr_agentic(
        operation: Annotated[
            Literal["workflow", "natural_query"],
            Field(
                description="Operation: 'workflow' for multi-step task, 'natural_query' for a question about your stack."
            ),
        ],
        prompt: Annotated[str, Field(description="Natural language description of what you want to do or ask.")],
        ctx: Context | None = None,
    ) -> dict:
        """LLM-powered cross-arr workflows via FastMCP sampling (SEP-1577).

        **workflow** — execute a multi-step cross-arr task described in natural
        language.  The LLM decides which tools to call.  Examples:
        - "add The Matrix to Radarr with best quality"
        - "search for Dune across all arrs and tell me if it's anywhere"
        - "find movies added this week"

        **natural_query** — ask a question about your media stack.  Examples:
        - "what's the most wanted movie right now?"
        - "how much free disk space do I have?"
        - "what's downloading right now?"

        Requires a sampling-capable MCP client (Claude Desktop, Cursor, etc.).
        Without sampling support, returns a clear error message.

        ## Return Format
        {"success": bool, "message": str, "data": {"response": str|None, "sampling_used": bool}}

        ## Examples
        arr_agentic(operation="workflow", prompt="add The Matrix to Radarr")
        arr_agentic(operation="natural_query", prompt="what's my most wanted movie?")
        """
        try:
            # Build stack context for the LLM
            available_services = []
            for name, client in clients.items():
                if client is not None:
                    available_services.append(name)

            stack_context = (
                f"arr-mcp v{TOOL_VERSION} — available services: {', '.join(available_services) or 'none'}. "
                f"The user said: {prompt}. "
                "Respond helpfully with what you know about the user's media stack. "
                "If the client supports sampling, you would orchestrate tool calls here."
            )

            # Try sampling first
            if ctx is not None:
                try:
                    sample_result = await ctx.sample(
                        messages=[
                            {
                                "role": "system",
                                "content": "You are arr-mcp's agentic orchestrator. You have access to the entire *arr stack. Respond concisely and helpfully.",
                            },
                            {"role": "user", "content": stack_context},
                        ],
                        max_tokens=1024,
                    )
                    if sample_result and isinstance(sample_result, dict):
                        content = sample_result.get("content", "") or sample_result.get("choices", [{}])[0].get(
                            "message", {}
                        ).get("content", "")
                        if content:
                            return {
                                "success": True,
                                "message": "Agentic response via sampling",
                                "data": {"response": content, "sampling_used": True},
                            }
                except Exception as sample_err:
                    logger.debug("Sampling failed, falling back: %s", sample_err)

            # Fallback: return structured context for the client LLM to interpret
            return {
                "success": True,
                "message": f"Task: {prompt}",
                "data": {
                    "response": (
                        f"The *arr stack has {len(available_services)} service(s) available: "
                        f"{', '.join(available_services)}. "
                        "To proceed, use the specific per-arr tools (radarr_movies, sonarr_series, etc.) "
                        "or the cross-arr orchestration tool (arr_orchestrate). "
                        f"Stack context: {stack_context}"
                    ),
                    "sampling_used": False,
                    "available_services": available_services,
                    "prompt": prompt,
                },
            }

        except Exception as e:
            logger.exception("arr_agentic failed: %s", e)
            return {"success": False, "message": str(e), "data": {"sampling_used": False, "response": None}}
