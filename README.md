> **PROTOTYP, nonprod.** Tracer Bullet für Bravo. Keine Kundendaten, keine Produktivnutzung.
> Ablaufdatum: 2027-02-24. Verantwortlich: lukas.sekoulidis@we-build-ai.de

# wbai-bravo-sample-proto

Kleine FastAPI-App (`/health`, `/items`), an der der asynchrone Bravo-Ablauf geprüft wird:
Issue → Cloud session → PR → Review → Merge → Sync nach Azure DevOps.

## Setup

```bash
make setup     # .venv, Abhängigkeiten, pre-commit
make verify    # black --check, ruff, pytest
make run       # uvicorn auf :8000
```

Abhängigkeiten ändern: `requirements.in` / `requirements-dev.in` anpassen, dann `make compile`.

## Variablen

Siehe `.env.example`. Alle optional; ohne `TEAMS_WEBHOOK_URL` / `BRAVO_KONTEXT_URL` sendet der
Stop-Hook keine Teams-Nachricht.

## Deployment

Keins. Der Prototyp läuft nur lokal und in CI.

## Weiter

- `CLAUDE.md`: Regeln für Claude-Sessions in diesem Repo
- `docs/RUNBOOK.md`: Ablauf für Menschen
- `docs/ASSUMPTIONS.md`: getroffene Annahmen
- `docs/HANDOFF.md`: Umsetzungsstand des Tracer Bullets
