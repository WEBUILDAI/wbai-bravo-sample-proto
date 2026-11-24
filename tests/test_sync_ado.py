"""Tests für scripts/sync-ado.sh gegen ein lokales Bare-Repo als Stand-in für Azure DevOps."""

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "sync-ado.sh"
GIT_ENV = {
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}


def _git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env={**os.environ, **GIT_ENV},
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


@pytest.fixture
def ado_remote(tmp_path: Path) -> Path:
    """Bare-Repo mit initialem main (wie ein frisch initialisiertes ADO-Repo)."""
    remote = tmp_path / "ado.git"
    _git("init", "-q", "--bare", "-b", "main", str(remote), cwd=tmp_path)
    seed = tmp_path / "seed"
    _git("clone", "-q", str(remote), str(seed), cwd=tmp_path)
    (seed / "README.md").write_text("ADO\n")
    (seed / "veraltet.txt").write_text("weg\n")
    _git("add", "-A", cwd=seed)
    _git("commit", "-q", "-m", "init", cwd=seed)
    _git("push", "-q", "origin", "HEAD:main", cwd=seed)
    return remote


def _run(remote: Path, tmp_path: Path, exclude: str | None = None) -> dict[str, str]:
    env = {
        **os.environ,
        **GIT_ENV,
        "ADO_REMOTE_URL": str(remote),
        "SYNC_WORKDIR": str(tmp_path / "work"),
        "GITHUB_OUTPUT": str(tmp_path / "gh-output"),
    }
    env.pop("ADO_TOKEN", None)
    if exclude is not None:
        exclude_file = tmp_path / "exclude.txt"
        exclude_file.write_text(exclude)
        env["SYNC_EXCLUDE_FILE"] = str(exclude_file)
    result = subprocess.run(
        ["bash", str(SCRIPT)], env=env, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    out = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    assert (tmp_path / "gh-output").read_text().splitlines()[-2:] == result.stdout.splitlines()
    return out


def _files(remote: Path, branch: str) -> set[str]:
    listing = _git("ls-tree", "-r", "--name-only", branch, cwd=remote)
    return set(listing.splitlines())


def test_sync_pushes_branch_with_committed_tree(ado_remote: Path, tmp_path: Path) -> None:
    """Given leere Exclude-Liste, when Sync, then sync/<sha> mit allen getrackten Dateien."""
    out = _run(ado_remote, tmp_path, exclude="# leer\n")
    short = _git("rev-parse", "--short=7", "HEAD", cwd=ROOT)
    assert out == {"branch": f"sync/{short}", "changed": "true"}
    files = _files(ado_remote, out["branch"])
    committed = set(_git("ls-tree", "-r", "--name-only", "HEAD", cwd=ROOT).splitlines())
    assert files == committed
    assert "veraltet.txt" not in files
    assert ".env" not in files


def test_sync_respects_exclude_list(ado_remote: Path, tmp_path: Path) -> None:
    """Given Kunden-Default als Exclude-Liste, when Sync, then .claude/, CLAUDE.md fehlen."""
    out = _run(ado_remote, tmp_path, exclude=".claude/\nCLAUDE.md  # Kommentar\n\n.mcp.json\n")
    files = _files(ado_remote, out["branch"])
    assert "CLAUDE.md" not in files
    assert not any(f.startswith(".claude/") for f in files)
    assert ".mcp.json" not in files
    assert "app/main.py" in files


def test_sync_without_changes_pushes_nothing(ado_remote: Path, tmp_path: Path) -> None:
    """Given ADO-main entspricht schon dem Stand, when Sync, then changed=false, kein Branch."""
    first = _run(ado_remote, tmp_path, exclude="")
    _git("push", "-q", ".", f"{first['branch']}:main", cwd=ado_remote)
    _git("branch", "-D", first["branch"], cwd=ado_remote)
    second = _run(ado_remote, tmp_path, exclude="")
    assert second["changed"] == "false"
    assert first["branch"] not in _git("branch", "--list", cwd=ado_remote)
