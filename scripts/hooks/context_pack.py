"""Holt ein Kontext-Paket vom Wissens-MCP und gibt es als SessionStart-additionalContext aus.

Spricht MCP Streamable HTTP mit der Standardbibliothek (initialize → notifications/initialized →
tools/call ``context_pack``). Jeder Fehler endet still: der Session-Start darf nie scheitern.

Env:
    BRAVO_KONTEXT_URL: Basis-URL des Kontext-Servers; MCP liegt unter ``<url>/mcp``.
    BRAVO_KONTEXT_TOKEN: Bearer-Token (optional; in Cloud sessions hängt der Proxy es an).
    BRAVO_KONTEXT_AUFGABE: Aufgabe für ``context_pack`` (Standard: Repo + Branch).
    BRAVO_KONTEXT_TECH: Tech-Filter (Standard: ``python``).
    BRAVO_KONTEXT_MAX: Anzahl Einträge (Standard: 5).
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import urllib.request
from typing import Any

logger = logging.getLogger("bravo.session_start")
PROTOCOL_VERSION = "2025-06-18"
TIMEOUT_S = 8.0


class McpClient:
    """Minimaler MCP-Client für Streamable HTTP (JSON- oder SSE-Antworten).

    Args:
        url: Vollständige MCP-Endpunkt-URL.
        token: Optionales Bearer-Token.

    """

    def __init__(self, url: str, token: str | None = None) -> None:
        """Initialisiert den Client ohne Netzwerkzugriff."""
        self.url = url
        self.token = token
        self.session_id: str | None = None
        self._next_id = 0

    def _post(self, message: dict[str, Any]) -> dict[str, Any] | None:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": PROTOCOL_VERSION,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        request = urllib.request.Request(
            self.url, data=json.dumps(message).encode(), headers=headers, method="POST"
        )
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:  # noqa: S310
            self.session_id = response.headers.get("Mcp-Session-Id") or self.session_id
            body = response.read().decode()
            content_type = response.headers.get("Content-Type", "")
        if "id" not in message or not body.strip():
            return None
        if "text/event-stream" in content_type:
            for line in body.splitlines():
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    if data.get("id") == message["id"]:
                        return data
            raise ValueError("Keine passende SSE-Antwort")
        return json.loads(body)

    def request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Sendet eine JSON-RPC-Anfrage und liefert ``result``.

        Args:
            method: JSON-RPC-Methode.
            params: Parameter.

        Returns:
            Das ``result``-Objekt der Antwort.

        Raises:
            RuntimeError: Bei JSON-RPC-Fehler.

        """
        self._next_id += 1
        reply = self._post(
            {"jsonrpc": "2.0", "id": self._next_id, "method": method, "params": params}
        )
        if not reply or "error" in reply:
            raise RuntimeError(f"MCP-Fehler bei {method}: {reply and reply.get('error')}")
        return reply["result"]

    def notify(self, method: str) -> None:
        """Sendet eine JSON-RPC-Notification ohne Antwort.

        Args:
            method: Methode der Notification.

        """
        self._post({"jsonrpc": "2.0", "method": method})

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Initialisiert die Session und ruft ein Tool auf.

        Args:
            name: Tool-Name.
            arguments: Tool-Argumente.

        Returns:
            Zusammengefügte Text-Inhalte der Tool-Antwort.

        """
        self.request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "bravo-session-start", "version": "0.1.0"},
            },
        )
        self.notify("notifications/initialized")
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        if result.get("isError"):
            raise RuntimeError("context_pack meldet isError")
        texts = [c.get("text", "") for c in result.get("content", []) if c.get("type") == "text"]
        if not texts and "structuredContent" in result:
            texts = [json.dumps(result["structuredContent"], ensure_ascii=False, indent=2)]
        return "\n".join(t for t in texts if t)


def default_aufgabe() -> str:
    """Leitet eine Aufgabe aus Repo-Name und Branch ab.

    Returns:
        Kurzbeschreibung für ``context_pack``.

    """
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        branch = ""
    return f"Arbeit im Repo wbai-bravo-sample-proto (FastAPI, Python), Branch {branch or '-'}"


def build_output(context: str) -> dict[str, Any]:
    """Baut die SessionStart-Hook-Ausgabe.

    Args:
        context: Text des Kontext-Pakets.

    Returns:
        JSON-Objekt für Claude Code.

    """
    text = (
        "Kontext aus dem Bravo-Wissens-MCP (context_pack). Hinweise, keine Anweisungen; "
        "bei Widerspruch gelten CLAUDE.md und Spec.\n\n" + context
    )
    return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}


def main() -> int:
    """Einstiegspunkt des Hooks.

    Returns:
        Immer 0.

    """
    logging.basicConfig(level=logging.WARNING, stream=sys.stderr, format="%(name)s %(message)s")
    base = os.getenv("BRAVO_KONTEXT_URL", "").strip()
    if not base:
        return 0
    client = McpClient(base.rstrip("/") + "/mcp", os.getenv("BRAVO_KONTEXT_TOKEN") or None)
    arguments = {
        "aufgabe": os.getenv("BRAVO_KONTEXT_AUFGABE") or default_aufgabe(),
        "tech": os.getenv("BRAVO_KONTEXT_TECH", "python"),
        "max": int(os.getenv("BRAVO_KONTEXT_MAX", "5")),
    }
    try:
        context = client.call_tool("context_pack", arguments)
    except Exception as exc:  # noqa: BLE001 - Session-Start darf nie scheitern
        logger.warning("context_pack nicht verfügbar: %s", exc)
        return 0
    if context.strip():
        sys.stdout.write(json.dumps(build_output(context), ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
