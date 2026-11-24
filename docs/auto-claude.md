# Auto-Claude (S8)

**[PROTOTYP]** `.claude/workflows/auto-claude.js` ist ein Spielzeug-Baum für das Workflow-Tool von
Claude Code: deterministische Orchestrierung mehrerer Subagenten statt eines einzelnen Agenten.

```
Plan ──► Slice A ─┐
     └─► Slice B ─┴─► Review
```

| Phase | Was | Ergebnis |
|---|---|---|
| Plan | Ein Agent liest Board oder Spec, schneidet genau zwei Slices (Maßstab: Skill `plan-to-issues`) | `{ziel, slices[2]}` |
| Slices | Zwei Agenten parallel; mit `dryRun: false` je eigener Git-Worktree, Branch `feature/<slug>`, PR gegen `main` | je `{status, branch, pr, verify}` |
| Review | Ein Agent prüft beide Slices gemeinsam (Barriere, weil er Überschneidungen sehen soll) | `{urteil, befunde[]}` |

## Starten
Nur in einer Session und nur, wenn ein Mensch den Workflow ausdrücklich verlangt
(Workflows können viele Agenten starten):

```text
Führe den Workflow auto-claude aus mit args { "spec": "docs/specs/0002-items-by-id.md" }
```

Standard ist `dryRun: true`: es wird nur geplant und beschrieben, nichts geändert.
Echt: `args { "board": 12, "dryRun": false }`.

## Grenzen
- Gerüst, nicht produktiv erprobt; `make verify` prüft nur Syntax und Phasen-Konsistenz
  (`tests/test_auto_claude.py`).
- Genau zwei Slices, keine Wiederholung bei rotem `verify` (der Stop-Hook greift in Subagenten
  nicht), kein Merge.
- Für automatische Läufe ohne Session siehe `bravo-implement.yml` (S10).

## Ausbauideen
- Adversariales Review (mehrere Reviewer, Mehrheitsentscheid).
- Slice-Anzahl aus dem Plan statt fest zwei.
- Nach dem Review: Nacharbeit-Schleife, bis keine Blocker mehr gemeldet werden.
