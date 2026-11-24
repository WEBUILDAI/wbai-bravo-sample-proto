"""Strukturtests für .claude/workflows/auto-claude.js (kein Ausführen der Agenten)."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".claude" / "workflows" / "auto-claude.js"


def test_meta_phases_match_phase_calls() -> None:
    """Given das Skript, when meta und phase()-Aufrufe verglichen, then Plan/Slices/Review."""
    source = WORKFLOW.read_text()
    assert source.count("export const meta") == 1
    meta = source[source.index("export const meta") : source.index("\n}\n")]
    meta_titles = re.findall(r"title: '([^']+)'", meta)
    called = re.findall(r"phase\('([^']+)'\)", source) + re.findall(r"phase: '([^']+)'", source)
    assert meta_titles == ["Plan", "Slices", "Review"]
    assert set(called) <= set(meta_titles)
    assert "Date.now" not in source and "Math.random" not in source


def test_dry_run_is_default() -> None:
    """Given keine args, when Skript läuft, then dryRun aktiv."""
    assert "const dryRun = input.dryRun !== false" in WORKFLOW.read_text()


@pytest.mark.skipif(shutil.which("node") is None, reason="node nicht installiert")
def test_script_parses_as_module(tmp_path: Path) -> None:
    """Given das Skript in async-Hülle, when node --check, then keine Syntaxfehler."""
    body = WORKFLOW.read_text().replace("export const meta", "const meta")
    wrapped = tmp_path / "wrapped.mjs"
    wrapped.write_text(f"export default async function run(args) {{\n{body}\n}}\n")
    result = subprocess.run(
        ["node", "--check", str(wrapped)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
