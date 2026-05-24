"""Smoke tests for the MCP server tool registration.

These tests do not hit Weaviate; they only assert the eight tools register
with stable names and that their handlers are callable. Live integration is
covered by tests/integration (testcontainers-backed).
"""

from __future__ import annotations

import asyncio

import pytest

from fractal_rag.server.mcp import build_server


EXPECTED_TOOLS = {
    "search_artifacts",
    "get_artifact",
    "near_artifact",
    "artifacts_by_concept",
    "list_concepts",
    "get_concept",
    "search_concepts",
    "corpus_stats",
}


def test_server_registers_eight_named_tools() -> None:
    mcp = build_server()
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert names == EXPECTED_TOOLS


def test_tool_descriptions_are_non_empty() -> None:
    mcp = build_server()
    tools = asyncio.run(mcp.list_tools())
    for t in tools:
        assert t.description and len(t.description) > 10, t.name


@pytest.mark.parametrize("tool_name", sorted(EXPECTED_TOOLS))
def test_each_tool_advertises_input_schema(tool_name: str) -> None:
    mcp = build_server()
    tools = asyncio.run(mcp.list_tools())
    tool = next(t for t in tools if t.name == tool_name)
    schema = tool.inputSchema
    assert schema is not None
    assert schema.get("type") == "object"
    assert "properties" in schema
