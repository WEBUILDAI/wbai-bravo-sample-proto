#!/usr/bin/env bash
# Setup-Skript für das Cloud environment wbai-bravo-proto und den Devcontainer.
# Aufruf: bash scripts/setup.sh. Idempotent: darf mehrfach laufen.
set -euo pipefail
cd "$(dirname "$0")/.."
make setup
