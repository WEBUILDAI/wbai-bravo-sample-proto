# Runbook: Async-Loop

Ablauf für Menschen. **[PROTOTYP, nonprod]**

```
Board-Issue → Slice-Sub-Issues → Cloud session je Board → PR je Slice → Review → Merge
            → Teams-Hinweis (Stop-Hook) → Sync nach Azure DevOps (S4)
```

## 1. Feature planen
1. Spec schreiben: `docs/specs/NNNN-<name>.md` (Ziel, Verhalten, Akzeptanzkriterien, Nicht-Ziele).
   Optional in einer Session mit dem Skill `plan-to-issues`.
2. Board-Issue mit Template **Board** anlegen, Spec verlinken.
3. Pro Slice ein Issue mit Template **Slice** anlegen und als Sub-Issue an das Board hängen
   (GitHub: Issue öffnen → „Create sub-issue“ bzw. „Add existing issue“).

## 2. Umsetzen lassen
```bash
claude --cloud "Board #<n> umsetzen"
```
Die Session liest Board, Spec und Slice-Issues, legt je Slice einen Branch `feature/…` an,
öffnet je Slice einen PR gegen `main` (Beschreibung beginnt mit `[PROTOTYP]`) und endet erst,
wenn `make verify` grün ist (Stop-Hook). Danach postet der Stop-Hook einen Teams-Hinweis.

Fortschritt ansehen: claude.ai/code oder `claude --resume`.

## 3. Review und Merge
- CI-Check `verify` muss grün sein.
- Annahmen in `docs/ASSUMPTIONS.md` lesen; offene Annahmen klären oder als Kommentar beantworten.
- Mergen macht immer ein Mensch. Agent-PRs werden nie automatisch gemerged.

## 4. Nach dem Merge
- `sync-ado.yml` spiegelt `main` als `sync/<short-sha>` nach Azure DevOps und öffnet dort einen PR
  (siehe `docs/output-sync.md`).

## Störungen
| Symptom | Ursache | Abhilfe |
|---|---|---|
| Session endet nicht, Stop-Hook meldet rot | `make verify` schlägt fehl | Fehler im Log der Session lesen, ggf. Hinweis per Kommentar ins Slice-Issue |
| `.venv fehlt` im Stop-Hook | Setup-Skript lief nicht | Cloud environment: Setup-Skript `bash scripts/setup.sh` eintragen |
| Kein Teams-Hinweis | `BRAVO_KONTEXT_URL`/`TEAMS_WEBHOOK_URL` fehlt | Network secret bzw. `.env` prüfen; ohne Variable ist der Hinweis absichtlich aus |
| CI-Check `verify` fehlt am PR | Branch-Schutz nicht gesetzt | `docs/branch-protection.md` |

## Beispiel
Spec `docs/specs/0001-items-filter.md` ist das Referenz-Feature: Board-Issue „Items nach Kategorie
filtern“ mit zwei Slice-Sub-Issues (Slice 1 Filter, Slice 2 Validierung).

## Automatische Läufe (S9, S10)
| Label | Wer setzt es | Was passiert |
|---|---|---|
| `triage` | Wissens-MCP (`vorschlag_anlegen`) oder Team | `bravo-triage.yml`: Rückfragen (`rueckfrage`) oder Triage-Ergebnis (`triage-ok`) als Kommentar |
| `ready` | immer ein Mensch | `bravo-implement.yml`: Branch `claude/issue-<n>-…`, `make verify`, PR gegen `main`, Label → `in-review` |

Beide Workflows laufen ohne die Repo-Variablen `ANTHROPIC_FEDERATION_RULE_ID` und
`ANTHROPIC_ORGANIZATION_ID` als grüner No-op. Fehlschläge kommentiert `bravo-implement` im Issue.
