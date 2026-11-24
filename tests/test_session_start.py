"""Tests für den SessionStart-Hook (scripts/hooks/on-session-start.sh, context_pack.py)."""

import json
import os
import subprocess
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "scripts" / "hooks" / "on-session-start.sh"


class FakeMcp:
    """Zustand des Fake-Servers: Modus und mitgeschnittene Anfragen."""

    def __init__(self) -> None:
        self.mode = "json"
        self.requests: list[tuple[dict[str, str], dict[str, Any]]] = []


def _handler(state: FakeMcp) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            pass

        def do_POST(self) -> None:  # noqa: N802
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            state.requests.append((dict(self.headers), body))
            if self.path != "/mcp" or state.mode == "fail":
                self.send_response(500)
                self.end_headers()
                return
            if "id" not in body:
                self.send_response(202)
                self.end_headers()
                return
            if body["method"] == "initialize":
                result: dict[str, Any] = {"protocolVersion": "2025-06-18", "capabilities": {}}
            else:
                args = body["params"]["arguments"]
                result = {"content": [{"type": "text", "text": f"Eintrag zu {args['tech']}"}]}
            reply = json.dumps({"jsonrpc": "2.0", "id": body["id"], "result": result})
            self.send_response(200)
            self.send_header("Mcp-Session-Id", "sess-1")
            if state.mode == "sse":
                self.send_header("Content-Type", "text/event-stream")
                payload = f"event: message\ndata: {reply}\n\n"
            else:
                self.send_header("Content-Type", "application/json")
                payload = reply
            self.end_headers()
            self.wfile.write(payload.encode())

    return Handler


@pytest.fixture
def fake_mcp() -> Iterator[tuple[str, FakeMcp]]:
    """Startet einen lokalen Fake-MCP-Server und liefert Basis-URL und Zustand."""
    state = FakeMcp()
    server = ThreadingHTTPServer(("127.0.0.1", 0), _handler(state))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}", state
    server.shutdown()


def _run(env_extra: dict[str, str]) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("BRAVO_", "CLAUDE_CODE"))}
    env.update({"CLAUDE_PROJECT_DIR": str(ROOT), "NO_PROXY": "127.0.0.1", **env_extra})
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        env.pop(key, None)
    return subprocess.run(
        ["bash", str(HOOK)], env=env, input="{}", capture_output=True, text=True, timeout=30
    )


def test_without_url_is_silent() -> None:
    """Given kein BRAVO_KONTEXT_URL, when Hook läuft, then keine Ausgabe, Exit 0."""
    result = _run({})
    assert result.returncode == 0
    assert result.stdout == ""


@pytest.mark.parametrize("mode", ["json", "sse"])
def test_outputs_additional_context(fake_mcp: tuple[str, FakeMcp], mode: str) -> None:
    """Given erreichbarer Server, when Hook läuft, then additionalContext mit Tool-Text."""
    url, state = fake_mcp
    state.mode = mode
    result = _run({"BRAVO_KONTEXT_URL": url + "/", "BRAVO_KONTEXT_TOKEN": "geheim"})
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "SessionStart"
    assert "Eintrag zu python" in output["additionalContext"]
    methods = [body.get("method") for _, body in state.requests]
    assert methods == ["initialize", "notifications/initialized", "tools/call"]
    headers, call = state.requests[-1]
    assert headers["Authorization"] == "Bearer geheim"
    assert headers["Mcp-Session-Id"] == "sess-1"
    assert call["params"]["name"] == "context_pack"
    assert set(call["params"]["arguments"]) == {"aufgabe", "tech", "max"}


def test_server_error_is_silent(fake_mcp: tuple[str, FakeMcp]) -> None:
    """Given Server antwortet 500, when Hook läuft, then keine stdout-Ausgabe, Exit 0."""
    url, state = fake_mcp
    state.mode = "fail"
    result = _run({"BRAVO_KONTEXT_URL": url})
    assert result.returncode == 0
    assert result.stdout == ""
    assert "context_pack nicht verfügbar" in result.stderr


def test_unreachable_server_is_silent() -> None:
    """Given Server nicht erreichbar, when Hook läuft, then Exit 0 ohne stdout."""
    result = _run({"BRAVO_KONTEXT_URL": "http://127.0.0.1:9"})
    assert result.returncode == 0
    assert result.stdout == ""


def test_mcp_json_points_to_kontext_server() -> None:
    """Given .mcp.json, when gelesen, then bravo-kontext per HTTP unter <URL>/mcp."""
    config = json.loads((ROOT / ".mcp.json").read_text())
    server = config["mcpServers"]["bravo-kontext"]
    assert server["type"] == "http"
    assert server["url"].startswith("${BRAVO_KONTEXT_URL")
    assert server["url"].endswith("/mcp")
