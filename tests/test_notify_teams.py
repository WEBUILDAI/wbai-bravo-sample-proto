"""Tests für den Adaptive-Card-Payload aus scripts/notify-teams.sh.

Das Skript läuft echt; `curl` wird durch einen Fake im PATH ersetzt, der seine Argumente als JSON
ablegt. So prüfen die Tests Payload, Ziel-URL und Header, ohne etwas zu senden.
"""

import json
import os
import stat
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "notify-teams.sh"

FAKE_CURL = f"""#!{sys.executable}
import json, os, sys
with open(os.environ["FAKE_CURL_OUT"], "w") as fh:
    json.dump(sys.argv[1:], fh)
"""


@pytest.fixture
def run_script(tmp_path: Path) -> Callable[..., list[str] | None]:
    """Startet notify-teams.sh mit Fake-curl und kontrollierter Umgebung."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    curl = bin_dir / "curl"
    curl.write_text(FAKE_CURL)
    curl.chmod(curl.stat().st_mode | stat.S_IEXEC)
    out = tmp_path / "curl-args.json"

    def _run(env_extra: dict[str, str], *args: str) -> list[str] | None:
        env = {
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "HOME": str(tmp_path),
            "BRAVO_ENV_FILE": str(tmp_path / "keine.env"),
            "FAKE_CURL_OUT": str(out),
            **env_extra,
        }
        result = subprocess.run(
            ["bash", str(SCRIPT), *args], env=env, capture_output=True, text=True, check=False
        )
        assert result.returncode == 0, result.stderr
        return json.loads(out.read_text()) if out.exists() else None

    return _run


def _payload(curl_args: list[str]) -> dict:
    return json.loads(curl_args[curl_args.index("-d") + 1])


def _card(curl_args: list[str]) -> dict:
    payload = _payload(curl_args)
    assert payload["type"] == "message"
    (attachment,) = payload["attachments"]
    assert attachment["contentType"] == "application/vnd.microsoft.card.adaptive"
    return attachment["content"]


def test_no_target_configured_sends_nothing(run_script: Callable[..., list[str] | None]) -> None:
    """Given weder Webhook noch Relay, when Skript läuft, then kein curl-Aufruf."""
    assert run_script({}, "Titel", "Text") is None


def test_card_payload_structure(run_script: Callable[..., list[str] | None]) -> None:
    """Given Webhook, when Skript läuft, then Adaptive Card 1.4 mit [PROTOTYP]-Titel und Fakten."""
    args = run_script(
        {"TEAMS_WEBHOOK_URL": "https://example.invalid/hook"}, "Session fertig", "make verify: grün"
    )
    assert args is not None
    assert args[-1] == "https://example.invalid/hook"
    card = _card(args)
    assert card["type"] == "AdaptiveCard"
    assert card["version"] == "1.4"
    title, facts = card["body"]
    assert title["type"] == "TextBlock"
    assert title["text"] == "[PROTOTYP] Session fertig"
    assert facts["type"] == "FactSet"
    values = {fact["title"]: fact["value"] for fact in facts["facts"]}
    assert set(values) == {"Repo", "Branch", "Ergebnis"}
    assert values["Ergebnis"] == "make verify: grün"
    assert values["Repo"]
    (action,) = card["actions"]
    assert action["type"] == "Action.OpenUrl"
    assert action["url"].startswith("https://github.com/")


def test_card_links_cloud_session(run_script: Callable[..., list[str] | None]) -> None:
    """Given eine Cloud-Session-ID, when Skript läuft, then Link auf die Session."""
    args = run_script(
        {
            "TEAMS_WEBHOOK_URL": "https://example.invalid/hook",
            "CLAUDE_CODE_REMOTE_SESSION_ID": "session_test123",
        },
        "T",
    )
    assert args is not None
    (action,) = _card(args)["actions"]
    assert action["url"] == "https://claude.ai/code/session_test123"


def test_card_escapes_special_characters(run_script: Callable[..., list[str] | None]) -> None:
    """Given Anführungszeichen und Umlaute im Text, when Skript läuft, then gültiges JSON."""
    text = 'Fehler: "x" & <y> \\ ü'
    args = run_script({"TEAMS_WEBHOOK_URL": "https://example.invalid/hook"}, "T", text)
    assert args is not None
    facts = _card(args)["body"][1]["facts"]
    assert facts[2]["value"] == text


def test_relay_uses_notify_path_and_bearer(run_script: Callable[..., list[str] | None]) -> None:
    """Given nur Relay mit Token, when Skript läuft, then POST an <url>/notify mit Bearer."""
    args = run_script(
        {"BRAVO_KONTEXT_URL": "https://kontext.example.invalid/", "BRAVO_KONTEXT_TOKEN": "t0k"},
        "T",
        "X",
    )
    assert args is not None
    assert args[-1] == "https://kontext.example.invalid/notify"
    assert "Authorization: Bearer t0k" in args
    assert _card(args)["body"][0]["text"] == "[PROTOTYP] T"


def test_webhook_wins_over_relay(run_script: Callable[..., list[str] | None]) -> None:
    """Given Webhook und Relay, when Skript läuft, then direkt an den Webhook ohne Bearer."""
    args = run_script(
        {
            "TEAMS_WEBHOOK_URL": "https://example.invalid/hook",
            "BRAVO_KONTEXT_URL": "https://kontext.example.invalid",
            "BRAVO_KONTEXT_TOKEN": "t0k",
        },
        "T",
    )
    assert args is not None
    assert args[-1] == "https://example.invalid/hook"
    assert not any(a.startswith("Authorization") for a in args)
