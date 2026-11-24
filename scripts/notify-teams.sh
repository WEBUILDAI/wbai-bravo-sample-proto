#!/usr/bin/env bash
# Postet eine kurze Adaptive Card in den Teams-Kanal wbai-bravo-proto.
# Aufruf: bash scripts/notify-teams.sh "<Titel>" "<Text>"
#
# Zwei Wege, der erste konfigurierte gewinnt:
#   1. TEAMS_WEBHOOK_URL   direkt an den Workflows-Webhook (lokal, aus .env)
#   2. BRAVO_KONTEXT_URL   Relay über das Wissens-MCP (POST <url>/notify). In Cloud sessions
#                          hängt der Proxy das Bearer-Token als Network secret an; lokal kommt
#                          es aus BRAVO_KONTEXT_TOKEN.
# Ist nichts gesetzt, tut das Skript nichts.
set -uo pipefail
cd "$(dirname "$0")/.."

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

title="${1:-Hinweis}"
text="${2:-}"
repo="$(git remote get-url origin 2>/dev/null | sed -E 's#.*github.com[:/]##; s#\.git$##')"
branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
link="https://github.com/${repo}/tree/${branch}"
[ -n "${CLAUDE_CODE_REMOTE_SESSION_ID:-}" ] && link="https://claude.ai/code/${CLAUDE_CODE_REMOTE_SESSION_ID}"

payload="$(TITLE="$title" TEXT="$text" REPO="$repo" BRANCH="$branch" LINK="$link" python3 - <<'PY'
import json, os
card = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.4",
    "body": [
        {"type": "TextBlock", "weight": "Bolder", "wrap": True,
         "text": f"[PROTOTYP] {os.environ['TITLE']}"},
        {"type": "FactSet", "facts": [
            {"title": "Repo", "value": os.environ["REPO"] or "-"},
            {"title": "Branch", "value": os.environ["BRANCH"] or "-"},
            {"title": "Ergebnis", "value": os.environ["TEXT"] or "-"},
        ]},
    ],
    "actions": [{"type": "Action.OpenUrl", "title": "Öffnen", "url": os.environ["LINK"]}],
}
print(json.dumps({"type": "message", "attachments": [
    {"contentType": "application/vnd.microsoft.card.adaptive", "content": card}]}))
PY
)"

if [ -n "${TEAMS_WEBHOOK_URL:-}" ]; then
  curl -fsS -m 10 -H "Content-Type: application/json" -d "$payload" "$TEAMS_WEBHOOK_URL" >/dev/null
elif [ -n "${BRAVO_KONTEXT_URL:-}" ]; then
  auth=()
  [ -n "${BRAVO_KONTEXT_TOKEN:-}" ] && auth=(-H "Authorization: Bearer ${BRAVO_KONTEXT_TOKEN}")
  curl -fsS -m 10 -H "Content-Type: application/json" "${auth[@]}" -d "$payload" \
    "${BRAVO_KONTEXT_URL%/}/notify" >/dev/null
fi
exit 0
