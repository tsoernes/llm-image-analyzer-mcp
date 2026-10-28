"""Offline transport, authentication and two-client regressions (no model/API calls)."""

from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
from fastmcp import Client, FastMCP

from llm_image_analyzer_mcp._shared_http import LocalTokenVerifier, transport_options


def private_token(tmp_path: Path) -> Path:
    path = tmp_path / "token"
    path.write_text("test-only-" + "x" * 48, encoding="utf-8")
    path.chmod(0o600)
    return path


def test_stdio_is_unchanged() -> None:
    assert transport_options(FastMCP("test")) == {"transport": "stdio"}


@pytest.mark.parametrize("port", [0, -1, 65536])
def test_bad_port_is_rejected(port: int, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="between"):
        transport_options(
            FastMCP("test"), http_port=port,
            http_token_file=str(private_token(tmp_path)),
        )


def test_authentication_cannot_be_omitted(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="requires --http-token-file"):
        transport_options(FastMCP("test"), http_port=8000)
    with pytest.raises(ValueError, match="requires --http-port"):
        transport_options(FastMCP("test"), http_token_file=str(private_token(tmp_path)))


def test_token_permissions_and_length(tmp_path: Path) -> None:
    path = private_token(tmp_path)
    path.chmod(0o644)
    with pytest.raises(ValueError, match="0600"):
        LocalTokenVerifier(str(path))
    path.chmod(0o600)
    path.write_text("short", encoding="utf-8")
    with pytest.raises(ValueError, match="at least 32"):
        LocalTokenVerifier(str(path))


@pytest.mark.asyncio
async def test_verifier(tmp_path: Path) -> None:
    path = private_token(tmp_path)
    verifier = LocalTokenVerifier(str(path))
    assert await verifier.verify_token("wrong") is None
    assert await verifier.verify_token("\u2603") is None
    assert await verifier.verify_token(path.read_text()) is not None


@pytest.fixture
def shared_server(tmp_path: Path) -> Iterator[tuple[str, str, int]]:
    token_file = private_token(tmp_path)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    code = """
import asyncio, os, sys
from fastmcp import FastMCP
from llm_image_analyzer_mcp._shared_http import transport_options
mcp = FastMCP("shared-test")
jobs = {}
tasks = set()
@mcp.tool()
async def probe(value: str, delay: float = 0.0) -> dict:
    await asyncio.sleep(delay)
    return {"value": value, "pid": os.getpid()}
@mcp.tool()
async def start_job(job_id: str) -> dict:
    async def work():
        await asyncio.sleep(0.2)
        jobs[job_id] = "done"
    jobs[job_id] = "running"
    task = asyncio.create_task(work())
    tasks.add(task)
    task.add_done_callback(tasks.discard)
    return {"job_id": job_id}
@mcp.tool()
async def job_status(job_id: str) -> dict:
    return {"status": jobs[job_id]}
mcp.run(**transport_options(mcp, http_port=int(sys.argv[1]), http_token_file=sys.argv[2]))
"""
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"))
    with (tmp_path / "server.log").open("w") as log:
        proc = subprocess.Popen(
            [sys.executable, "-c", code, str(port), str(token_file)],
            env=env, stdout=log, stderr=log,
        )
        try:
            url = f"http://127.0.0.1:{port}"
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    pytest.fail((tmp_path / "server.log").read_text())
                try:
                    if httpx.get(url + "/healthz", timeout=0.3).status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.05)
            else:
                pytest.fail("Shared test server did not start")
            yield url, token_file.read_text(), proc.pid
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


@pytest.mark.asyncio
async def test_two_clients_share_one_process_without_request_leakage(
    shared_server: tuple[str, str, int],
) -> None:
    url, token, pid = shared_server
    async with httpx.AsyncClient() as http:
        assert (await http.get(url + "/healthz")).json()["pid"] == pid
        assert (await http.post(url + "/mcp", json={})).status_code == 401
        assert (await http.post(
            url + "/mcp", json={}, headers={"Authorization": "Bearer wrong"}
        )).status_code == 401
    async with Client(url + "/mcp", auth=token) as first:
        async with Client(url + "/mcp", auth=token) as second:
            slow = asyncio.create_task(first.call_tool(
                "probe", {"value": "first", "delay": 0.5}
            ))
            fast = await second.call_tool("probe", {"value": "second"})
            assert not slow.done(), "A slow client must not block other requests"
            assert fast.data == {"value": "second", "pid": pid}
            assert (await slow).data == {"value": "first", "pid": pid}
            await second.call_tool("start_job", {"job_id": "survives-disconnect"})
        # The second session disconnects while its background job is running.
        await asyncio.sleep(0.4)
        result = await first.call_tool("job_status", {"job_id": "survives-disconnect"})
        assert result.data == {"status": "done"}
        assert (await first.call_tool("probe", {"value": "still-connected"})).data["pid"] == pid
