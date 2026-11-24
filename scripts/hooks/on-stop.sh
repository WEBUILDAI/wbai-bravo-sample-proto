#!/usr/bin/env bash
# Stop-Hook: "fertig" nur bei grünem `make verify`.
# - Rot und noch kein Stop-Hook-Durchlauf aktiv: blockiert (Exit 2), Claude bekommt die Fehler.
# - Rot und stop_hook_active=true: nicht erneut blockieren (keine Endlosschleife), nur melden.
# - Danach Teams-Hinweis über scripts/notify-teams.sh (nur in Cloud sessions oder mit BRAVO_NOTIFY=always).
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"

input="$(cat || true)"
active="$(printf '%s' "$input" | python3 -c 'import json,sys
try: print(str(json.load(sys.stdin).get("stop_hook_active", False)).lower())
except Exception: print("false")')"

if [ ! -x .venv/bin/pytest ]; then
  echo "make verify nicht möglich: .venv fehlt. Erst 'make setup' ausführen." >&2
  [ "$active" = "true" ] && exit 0
  exit 2
fi

log="$(make verify 2>&1)"
status=$?
result="grün"
[ $status -ne 0 ] && result="rot"

if [ "$result" = "rot" ] && [ "$active" != "true" ]; then
  {
    echo "make verify ist rot. Bitte beheben, bevor die Aufgabe als fertig gilt."
    printf '%s\n' "$log" | tail -n 40
  } >&2
  exit 2
fi

if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || [ "${BRAVO_NOTIFY:-}" = "always" ]; then
  bash scripts/notify-teams.sh "Session fertig" "make verify: $result" || true
fi
exit 0
