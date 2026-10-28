# Shared local MCP service

The default CLI still uses stdio. Shared mode uses a single FastMCP process,
authenticated Streamable HTTP on **127.0.0.1:8793/mcp**. No packages need to be
installed if this checkout's existing virtual environment is ready.

## Run

```fish
# First provision a random bearer token in a user-owned mode-0600 file.
# Never put tokens on command lines, in logs, or in this repository.
.venv/bin/python -m llm_image_analyzer_mcp.server \
    --http-port 8793 \
    --http-token-file $HOME/.config/shared-mcp/llm-image-analyzer.token
```

`deploy/shared-http.service` is a systemd **user** unit template. Adjust
`%h/code/llm-image-analyzer` if your checkout is elsewhere. The environment file is private
(mode 0600) and contains the existing stdio server's environment overrides.
Application .env loading and model selection remain unchanged. Do not copy
credentials from a config into a tracked file.

Copy the unit to `~/.config/systemd/user/mcp-llm-image-analyzer.service`, then use
`systemctl --user daemon-reload` and
`systemctl --user enable --now mcp-llm-image-analyzer.service`.
This starts at user-service startup; it does not enable user lingering.

## Codex connection

In the existing `[mcp_servers."llm-image-analyzer"]` table, replace command/args/env with
`url = "http://127.0.0.1:8793/mcp"` and configure an Authorization bearer
header privately (or use Codex's environment-backed bearer-token option).
Preserve timeouts and per-tool approvals. Validate the new connection before
closing old sessions. The unauthenticated `/healthz` endpoint returns only the
service name, status and process ID; all MCP operations require the bearer token.

## Sharing boundary and lifecycle

* This is for **one trusted OS user**, not different users/tenants. All authorized
  clients share credentials, model configuration, caches and job registries.
  Jobs are service-wide, not session-private; cancellation by ID retains existing
  behavior. UUID job identities remain distinct.
* Use explicit **absolute paths** in tool arguments. HTTP cannot inherit each
  client's working directory; the service working directory is fixed.
* One worker only: do not add multiple Uvicorn workers, which would duplicate
  memory and split the in-memory job registry.
* Disconnecting an HTTP client does not shut down the process or its detached
  background work. Restarting/stopping the service can interrupt work and loses
  existing ephemeral job records: inspect active jobs first.
* Authentication is mandatory in HTTP mode; missing/short/publicly readable token
  files fail closed. There is deliberately no public bind option. Do not proxy
  this endpoint onto the network.
* Existing stdio processes are NOT killed during migration. They retain their
  live connections/jobs and disappear as the old clients exit/reconnect. Memory
  savings are therefore gradual, not an immediate guaranteed amount.
* Roll back by restoring the pre-migration Codex config, reconnecting clients,
  and stopping/disabling the shared service only after checking its jobs.

## Offline verification

```fish
env PYTHONPATH=src .venv/bin/python -m pytest tests/test_shared_http.py -q
```

Covers mandatory auth, private token permissions, stdio compatibility, distinct
concurrent client requests in one PID, and background work surviving a disconnect.
No model inference, indexing, external API call, or paid job is needed.
