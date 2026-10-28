"""Authenticated, loopback-only shared MCP transport; stdio remains the default.

This service is shared by trusted clients of ONE OS user, not a multi-tenant API.
Credentials, job registries and model configuration are service-wide. Never expose
it via an ingress/proxy or bind to a non-loopback interface.
"""

from __future__ import annotations

import os
import stat
from hmac import compare_digest
from pathlib import Path
from typing import Literal, TypedDict

from typing_extensions import override

from fastmcp import FastMCP
from fastmcp.server.auth import TokenVerifier
from fastmcp.server.auth.auth import AccessToken
from starlette.requests import Request
from starlette.responses import JSONResponse


class LocalTokenVerifier(TokenVerifier):
    """Validate a private local bearer token without logging its value."""

    def __init__(self, token_file: str) -> None:
        super().__init__()
        path = Path(token_file).expanduser()
        info = path.stat()
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("HTTP token must be a regular file")
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise ValueError("HTTP token file must be owned by this user and mode 0600")
        self._token: bytes = path.read_text(encoding="utf-8").strip().encode("utf-8")
        if len(self._token) < 32:
            raise ValueError("HTTP token must contain at least 32 bytes")

    @override
    async def verify_token(self, token: str) -> AccessToken | None:
        if not compare_digest(token.encode("utf-8"), self._token):
            return None
        return AccessToken(token=token, client_id="local-codex", scopes=[])


class TransportOptions(TypedDict, total=False):
    transport: Literal["stdio", "streamable-http"]
    host: str
    port: int
    path: str
    stateless_http: bool
    show_banner: bool


def transport_options(
    server: FastMCP,
    *,
    http_port: int | None = None,
    http_token_file: str | None = None,
) -> TransportOptions:
    """Select stdio, or explicitly authenticated HTTP with no public bind option."""
    if http_port is None:
        if http_token_file is not None:
            raise ValueError("--http-token-file requires --http-port")
        return {"transport": "stdio"}
    if not 1 <= http_port <= 65535:
        raise ValueError("--http-port must be between 1 and 65535")
    if http_token_file is None:
        raise ValueError("--http-port requires --http-token-file")
    server.auth = LocalTokenVerifier(http_token_file)

    @server.custom_route("/healthz", methods=["GET"])
    async def healthz(_request: Request) -> JSONResponse:
        # Deliberately minimal and unprivileged; /mcp still requires bearer auth.
        return JSONResponse(
            {"status": "ok", "pid": os.getpid(), "service": server.name}
        )

    return {
        "transport": "streamable-http",
        "host": "127.0.0.1",
        "port": http_port,
        "path": "/mcp",
        "stateless_http": False,
        "show_banner": False,
    }
