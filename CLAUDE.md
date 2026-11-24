# CLAUDE.md

Prototyp (nonprod) für Bravo. FastAPI-Sample, Python 3.12.

## Befehle
- `make setup`: venv + Abhängigkeiten + pre-commit
- `make verify`: black --check, ruff, pytest. Muss vor "fertig" grün sein (Stop-Hook prüft das).
- `make format`: black + ruff --fix
- Abhängigkeiten nur in `requirements*.in`, danach `make compile`. Nie `pip install` direkt.

## Code
- `app/main.py`: FastAPI-App, `app/logging_config.py`: Logging. Kein `print`, immer `logging`.
- Google-Docstrings, Typen überall, Zeilenlänge 100.
- Tests in `tests/`, je Endpunkt mindestens ein Test, `fastapi.testclient.TestClient`.

## Ablauf
- Arbeit kommt als GitHub Issue (Template "Slice"). Ein Slice = ein PR.
- Branches: `feature/…`, `bugfix/…`, `hotfix/…`, `chore/…`; automatisierte Läufe `claude/…`.
- PRs gehen direkt auf `main` (Prototyp-Abweichung). Beschreibung beginnt mit `[PROTOTYP]`.
- Specs in `docs/specs/NNNN-<name>.md`, Entscheidungen in `docs/decisions/`.
- Jede Annahme in `docs/ASSUMPTIONS.md` eintragen.

## Grenzen
- Nie mergen, nie force-pushen, keine Azure-Ressourcen anlegen oder löschen, kein `pulumi up`.
- Keine Secrets in Dateien. `.env` ist lokal und nicht lesbar.
- Commits und PRs ohne Hinweise auf KI-Werkzeuge oder Session-Links.
