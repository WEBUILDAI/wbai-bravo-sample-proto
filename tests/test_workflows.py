"""Strukturtests für die Agent-Workflows unter .github/workflows/ (Guards, Auth, Grenzen)."""

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
AGENT_WORKFLOWS = sorted(WORKFLOWS.glob("bravo-*.yml"))


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text())
    # PyYAML liest den Schlüssel `on` als True.
    data["on"] = data.pop(True, data.get("on"))
    return data


def _claude_step(data: dict[str, Any]) -> dict[str, Any]:
    steps = [s for job in data["jobs"].values() for s in job["steps"]]
    (step,) = [s for s in steps if str(s.get("uses", "")).startswith("anthropics/claude-code")]
    return step


def test_all_workflows_parse() -> None:
    """Given alle Workflows, when YAML geladen, then je mindestens ein Job."""
    for path in WORKFLOWS.glob("*.yml"):
        assert _load(path)["jobs"], path.name


@pytest.mark.parametrize("path", AGENT_WORKFLOWS, ids=lambda p: p.name)
def test_agent_workflow_uses_wif_without_api_key(path: Path) -> None:
    """Given Agent-Workflow, when geprüft, then WIF aus Repo-Variablen, kein API-Key."""
    text = path.read_text()
    assert "anthropic_api_key" not in text
    assert "secrets." not in text
    data = _load(path)
    assert data["permissions"]["id-token"] == "write"
    inputs = _claude_step(data)["with"]
    assert inputs["anthropic_federation_rule_id"] == "${{ vars.ANTHROPIC_FEDERATION_RULE_ID }}"
    assert inputs["anthropic_organization_id"] == "${{ vars.ANTHROPIC_ORGANIZATION_ID }}"
    assert _claude_step(data)["uses"] == "anthropics/claude-code-action@v1"


@pytest.mark.parametrize("path", AGENT_WORKFLOWS, ids=lambda p: p.name)
def test_agent_workflow_limits(path: Path) -> None:
    """Given Agent-Workflow, when geprüft, then timeout, max-turns, kein freies Bash."""
    data = _load(path)
    for job in data["jobs"].values():
        assert 0 < job["timeout-minutes"] <= 60
    args = _claude_step(data)["with"]["claude_args"]
    assert re.search(r"--max-turns \d+", args)
    allowed = re.search(r'--allowedTools "([^"]+)"', args)
    assert allowed
    tools = [t.strip() for t in allowed.group(1).split(",")]
    assert "Bash" not in tools
    assert all(t != "Bash(*)" for t in tools)


def test_triage_guard() -> None:
    """Given bravo-triage, when Guard geprüft, then Rollen, MCP-Bot, nie claude[bot]."""
    data = _load(WORKFLOWS / "bravo-triage.yml")
    assert set(data["on"]) == {"issues", "issue_comment"}
    condition = data["jobs"]["triage"]["if"]
    for token in (
        '"OWNER","MEMBER","COLLABORATOR"',
        "wbai-bravo-mcp-proto[bot]",
        "github.event.comment.user.login != 'claude[bot]'",
        "github.event.label.name == 'triage'",
        "github.event.issue.pull_request == null",
    ):
        assert token in condition
    prompt = _claude_step(data)["with"]["prompt"]
    assert "Setze niemals das Label `ready`" in prompt
