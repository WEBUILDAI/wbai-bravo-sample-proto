#!/usr/bin/env bash
# Spiegelt den committeten Stand (HEAD) dieses Repos als Branch sync/<short-sha> in ein Ziel-Repo
# (Azure DevOps). Der PR im Ziel wird separat angelegt (Workflow sync-ado.yml, `az repos pr create`).
#
# Eingaben (Env):
#   ADO_REMOTE_URL   Git-URL des Ziel-Repos (Pflicht; in Tests auch ein lokaler Pfad)
#   ADO_TOKEN        Entra-Access-Token für Azure DevOps (optional, als Bearer-Header; nie in URL)
#   SYNC_EXCLUDE_FILE  Exclude-Liste (Standard: .github/ado-sync-exclude.txt)
#   SYNC_TARGET_BRANCH Ziel-Branch im ADO-Repo (Standard: main)
#   SYNC_WORKDIR     Arbeitsverzeichnis für den Klon (Standard: mktemp)
#
# Ausgaben: Zeilen `branch=…` und `changed=true|false` auf stdout und, falls gesetzt, in
# $GITHUB_OUTPUT.
set -euo pipefail
cd "$(dirname "$0")/.."

: "${ADO_REMOTE_URL:?ADO_REMOTE_URL fehlt}"
exclude_file="${SYNC_EXCLUDE_FILE:-.github/ado-sync-exclude.txt}"
target="${SYNC_TARGET_BRANCH:-main}"
workdir="${SYNC_WORKDIR:-$(mktemp -d)}"
sha="$(git rev-parse HEAD)"
short="$(git rev-parse --short=7 HEAD)"
branch="sync/${short}"

git_ado() {
  if [ -n "${ADO_TOKEN:-}" ]; then
    git -c http.extraheader="AUTHORIZATION: bearer ${ADO_TOKEN}" "$@"
  else
    git "$@"
  fi
}

pathspec=(.)
if [ -f "$exclude_file" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%%#*}"
    line="$(printf '%s' "$line" | xargs)"
    [ -z "$line" ] && continue
    pathspec+=(":(exclude)${line%/}")
  done <"$exclude_file"
fi

dest="${workdir}/ado"
rm -rf "$dest"
git_ado clone -q --branch "$target" --single-branch "$ADO_REMOTE_URL" "$dest"
git -C "$dest" checkout -q -b "$branch"
# Ziel komplett leeren (außer .git), dann den GitHub-Stand ohne Excludes hineinlegen.
find "$dest" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
git archive --format=tar HEAD -- "${pathspec[@]}" | tar -x -C "$dest"
git -C "$dest" add -A

changed=true
if git -C "$dest" diff --cached --quiet; then
  changed=false
else
  git -C "$dest" \
    -c user.name="wbai-bravo-sync" -c user.email="wbai-bravo-sync@users.noreply.github.com" \
    commit -q -m "[PROTOTYP] Sync von GitHub ${short}" -m "Quelle: ${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-WEBUILDAI/wbai-bravo-sample-proto}/commit/${sha}"
  git_ado -C "$dest" push -q origin "$branch"
fi

printf 'branch=%s\nchanged=%s\n' "$branch" "$changed"
if [ -n "${GITHUB_OUTPUT:-}" ]; then
  printf 'branch=%s\nchanged=%s\n' "$branch" "$changed" >>"$GITHUB_OUTPUT"
fi
