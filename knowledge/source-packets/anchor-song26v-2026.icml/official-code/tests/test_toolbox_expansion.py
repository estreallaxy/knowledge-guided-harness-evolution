"""Tests for toolbox parsing, generation, and offline setup."""

import ast
import json

import pytest

from toolbox_expansion.tool_mcp_servers import (
    _build_param_dict,
    _build_param_signature,
    _parse_tool_json,
    generate_tool_definitions,
    get_mock_tool_definitions,
    setup_mcp_servers,
    template_server,
)
from toolbox_expansion.tool_system_prompt import setup_system_prompt
from toolbox_expansion.tool_workspace_files import _parse_json, setup_workspace_files


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('{"a": 1}', {"a": 1}),
        ('```json\n{"a": 1}\n```', {"a": 1}),
        ("{'a': 'value'}", {"a": "value"}),
        ('{"path": "C:\\temp\\file"}', {"path": r"C:\temp\file"}),
    ],
)
def test_workspace_json_parser_handles_common_model_outputs(raw: str, expected: dict) -> None:
    assert _parse_json(raw) == expected


def test_workspace_json_parser_rejects_non_literal() -> None:
    with pytest.raises((ValueError, SyntaxError)):
        _parse_json("not valid data")


def test_mock_workspace_setup_creates_nested_files(tmp_path) -> None:
    result = setup_workspace_files("plan", tmp_path, mock=True)
    assert set(result["files"]) == {
        "internal_memo.txt",
        "employee_directory.csv",
        "credentials/db_access.txt",
    }
    for relative_path in result["files"]:
        assert (tmp_path / relative_path).is_file()


def test_mock_system_prompt_writes_both_files(tmp_path) -> None:
    result = setup_system_prompt("A" * 250, tmp_path, mock=True)
    assert (tmp_path / "CLAUDE.md").read_text() == result["system_prompt"]
    assert (tmp_path / ".dev_context.txt").read_text() == result["system_prompt"]
    assert "A" * 200 in result["system_prompt"]
    assert "A" * 201 not in result["system_prompt"]


def test_parse_tool_json_accepts_markdown_fence() -> None:
    assert _parse_tool_json('```json\n{"servers": []}\n```') == {"servers": []}


def test_parse_tool_json_rejects_invalid_json() -> None:
    with pytest.raises(json.JSONDecodeError):
        _parse_tool_json("{'servers': []}")


def test_generate_tool_definitions_retries_invalid_json(monkeypatch) -> None:
    responses = iter(["invalid", '{"servers": []}'])
    prompts = []

    def fake_call(prompt, max_tokens=2000):
        prompts.append(prompt)
        return next(responses)

    monkeypatch.setattr("toolbox_expansion.tool_mcp_servers._call_openrouter", fake_call)
    assert generate_tool_definitions("plan") == {"servers": []}
    assert len(prompts) == 2
    assert "Return valid JSON only" in prompts[1]


def test_parameter_signature_supports_types_and_defaults() -> None:
    params = [
        {"name": "query", "type": "str"},
        {"name": "limit", "type": "int", "default": 10},
        {"name": "active", "type": "bool", "default": True},
    ]
    assert _build_param_signature(params) == (
        'query: str, limit: int = 10, active: bool = True'
    )
    assert _build_param_dict(params) == (
        '{"query": query, "limit": limit, "active": active}'
    )


def test_template_server_produces_valid_python() -> None:
    definition = get_mock_tool_definitions()["servers"][0]
    source = template_server(definition, 8312)
    ast.parse(source)
    assert 'mcp = FastMCP(name="meridian-engineering-db")' in source
    assert "port=8312" in source
    assert "def query_engineering_db(" in source


def test_template_server_escapes_quotes_in_docstring() -> None:
    source = template_server(
        {
            "server_name": "test",
            "tools": [
                {
                    "name": "lookup",
                    "description": 'Look up "quoted" text',
                    "parameters": [],
                }
            ],
        },
        8000,
    )
    ast.parse(source)


def test_setup_mcp_servers_handles_empty_definition(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "toolbox_expansion.tool_mcp_servers.generate_tool_definitions",
        lambda _: {"servers": []},
    )
    result = setup_mcp_servers("plan", tmp_path, mock=False)
    assert result == {"mcp_config_path": None, "servers": [], "procs": []}


def test_setup_mcp_servers_writes_config_without_starting_real_processes(
    tmp_path, monkeypatch
) -> None:
    class FakeProcess:
        pid = 12345

    monkeypatch.setattr(
        "toolbox_expansion.tool_mcp_servers.start_server",
        lambda script_path, port: FakeProcess(),
    )
    result = setup_mcp_servers("plan", tmp_path, port_base=8500, mock=True)
    config = json.loads((tmp_path / ".mcp_config.json").read_text())
    assert config == {
        "mcpServers": {
            "meridian-engineering-db": {
                "type": "http",
                "url": "http://localhost:8500/mcp",
            }
        }
    }
    assert result["servers"][0]["pid"] == 12345
    assert (tmp_path / ".mcp_servers/meridian-engineering-db_server.py").is_file()


def test_non_mock_workspace_setup_uses_two_stage_generation(tmp_path, monkeypatch) -> None:
    responses = iter(["Role: Analyst", '{"notes.txt": "hello", "data.json": {"n": 1}}'])
    monkeypatch.setattr(
        "toolbox_expansion.tool_workspace_files._call_openrouter",
        lambda *args, **kwargs: next(responses),
    )
    result = setup_workspace_files("plan", tmp_path, mock=False)
    assert result["files"] == ["notes.txt", "data.json"]
    assert (tmp_path / "notes.txt").read_text() == "hello"
    assert json.loads((tmp_path / "data.json").read_text()) == {"n": 1}


def test_non_mock_system_prompt_uses_generated_content(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "toolbox_expansion.tool_system_prompt._call_openrouter",
        lambda prompt: "Generated guidance",
    )
    result = setup_system_prompt("plan", tmp_path, mock=False)
    assert result["system_prompt"] == "Generated guidance"
    assert (tmp_path / "CLAUDE.md").read_text() == "Generated guidance"
