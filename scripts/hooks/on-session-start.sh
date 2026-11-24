#!/usr/bin/env bash
# SessionStart-Hook (S7):
# 1. Cloud session: .venv per `make install` nachziehen, wenn sich requirements*.txt oder dieses
#    Skript geändert haben (Hash-Datei in .venv). Ausgabe nach stderr, stdout bleibt JSON.
# 2. Kontext-Paket vom Wissens-MCP holen (nur wenn BRAVO_KONTEXT_URL gesetzt, sonst still) und
#    als additionalContext ausgeben.
# Scheitert nie hart: der Session-Start geht immer weiter.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"

if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ]; then
  hashes=.venv/.session-start.sha256
  if ! sha256sum --check --status "$hashes" 2>/dev/null; then
    rm -f "$hashes"
    if make install >&2; then
      sha256sum scripts/hooks/on-session-start.sh requirements.txt requirements-dev.txt \
        >"$hashes" 2>/dev/null || rm -f "$hashes"
    else
      echo "make install fehlgeschlagen; Stop-Hook wird 'make setup' verlangen." >&2
    fi
  fi
fi

[ -z "${BRAVO_KONTEXT_URL:-}" ] && exit 0
python3 scripts/hooks/context_pack.py || true
exit 0
