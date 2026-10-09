"""Tests for the backend LLM proxy (POST /api/llm/chat, POST /api/chat).

The proxy keeps provider keys server-side; Ollama/LM Studio are mocked with
pytest-httpx. (A live-Ollama 500 during development proved the error relay;
these tests prove the success path parsing.)
"""

import pytest

from arr_mcp.api import _forward_llm_chat, create_api_router


@pytest.mark.asyncio
async def test_forward_ollama_chat_parses_reply(httpx_mock):
    httpx_mock.add_response(
        url="http://127.0.0.1:11434/api/chat",
        method="POST",
        json={"message": {"content": "PROXY-OK"}},
    )
    reply = await _forward_llm_chat("ollama", "http://127.0.0.1:11434", "llama3.2", [{"role": "user", "content": "hi"}])
    assert reply == "PROXY-OK"


@pytest.mark.asyncio
async def test_forward_lmstudio_chat_parses_reply(httpx_mock):
    httpx_mock.add_response(
        url="http://127.0.0.1:1234/v1/chat/completions",
        method="POST",
        json={"choices": [{"message": {"content": "PROXY-OK"}}]},
    )
    reply = await _forward_llm_chat("lmstudio", "http://127.0.0.1:1234", "model", [{"role": "user", "content": "hi"}])
    assert reply == "PROXY-OK"


def test_router_exposes_llm_and_skill_routes():
    router = create_api_router({})
    paths = sorted({r.path for r in router.routes})
    for expected in (
        "/api/capabilities",
        "/api/skills",
        "/api/v1/diagnostics",
        "/api/llm/discover",
        "/api/llm/providers",
        "/api/llm/models",
        "/api/llm/onboarding",
        "/api/llm/chat",
        "/api/chat",
    ):
        assert expected in paths, f"missing route {expected}"
