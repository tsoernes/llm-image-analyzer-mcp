"""CLI compatibility regressions, without opening sockets or calling models."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from fastmcp import FastMCP

from llm_image_analyzer_mcp import server


@pytest.mark.parametrize("http", [False, True])
def test_main_selects_transport(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, http: bool,
) -> None:
    token = tmp_path / "token"
    _ = token.write_text("test-only-" + "x" * 48)
    token.chmod(0o600)
    instance = FastMCP("entrypoint-test")
    run = Mock()
    monkeypatch.setattr(instance, "run", run)
    monkeypatch.setattr(server, "mcp", instance)
    argv = ["server"]
    if http:
        argv += ["--http-port", "8799", "--http-token-file", str(token)]
    monkeypatch.setattr("sys.argv", argv)

    server.main()
    assert run.call_count == 1
    assert run.call_args.kwargs["transport"] == ("streamable-http" if http else "stdio")
    if http:
        assert run.call_args.kwargs["host"] == "127.0.0.1"
        assert run.call_args.kwargs["port"] == 8799
        assert instance.auth is not None
