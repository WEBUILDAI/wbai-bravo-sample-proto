---
name: plan-to-issues
description: Zerlegt eine Spec aus docs/specs/ in ein Board-Issue und Slice-Sub-Issues nach den Templates board.yml und slice.yml. Verwenden, wenn ein Feature geplant, eine Spec in Issues übersetzt oder „Board anlegen“ / „in Slices schneiden“ verlangt wird.
---

# plan-to-issues

**[PROTOTYP]** Aus einer Spec wird ein Board-Issue mit Slice-Sub-Issues. Ein Slice = ein PR.

## Ablauf
1. **Spec lesen** (`docs/specs/NNNN-<name>.md`). Fehlt sie, zuerst eine Spec im Format von
   `docs/specs/README.md` entwerfen (Ziel, Verhalten, Akzeptanzkriterien, Nicht-Ziele) und als
   eigenen PR vorschlagen. Ohne Spec keine Issues.
2. **Kontext holen**: Ist das MCP `bravo-kontext` verbunden, `context_pack(aufgabe=<Spec-Ziel>,
   tech="python")` aufrufen und relevante Muster/Fallstricke bei den Slices berücksichtigen.
3. **Schneiden**. Jeder Slice
   - ist vertikal (Endpunkt + Test + Doku), nicht horizontal (erst alle Modelle, dann alle Tests),
   - endet mit grünem `make verify`,
   - ist in einer Cloud session in unter ~1 h umsetzbar,
   - deckt nachvollziehbar Akzeptanzkriterien der Spec ab (jedes Kriterium genau einem Slice),
   - nennt Abhängigkeiten zu anderen Slices explizit.
   Zwei bis fünf Slices. Mehr → Spec teilen.
4. **Entwurf zeigen** als Markdown: Board-Titel, Ziel, Slice-Liste mit Akzeptanzkriterien.
   In unbeaufsichtigten Läufen ohne Rückfrage weitermachen und Annahmen in
   `docs/ASSUMPTIONS.md` notieren.
5. **Anlegen** (nur wenn Schreibrechte auf Issues vorhanden sind; Cloud sessions im Prototyp
   legen keine Board-Issues an, dann den Entwurf als Datei `docs/specs/NNNN-<name>.issues.md`
   ablegen und im PR erwähnen):
   - Board-Issue mit Feldern aus `.github/ISSUE_TEMPLATE/board.yml`, Label `board`.
   - Je Slice ein Issue mit Feldern aus `slice.yml`, Label `slice`, Titel `[Slice] …`.
   - Slices als Sub-Issues an das Board hängen.
6. **Abschluss**: Liste der Issue-Nummern und der Startbefehl
   `claude --cloud "Board #<n> umsetzen"` (siehe `docs/RUNBOOK.md`).

## Format Slice-Issue
```markdown
### Board-Issue
#<board>
### Spec-Abschnitt
docs/specs/NNNN-<name>.md#verhalten
### Aufgabe
<was sich ändert>
### Akzeptanzkriterien
- Given …, when …, then …
### Branch-Typ
feature
### Hinweise
<Dateien, Abhängigkeiten>
```

## Nicht tun
- Keine Issues ohne Spec, keine Slices ohne Tests.
- Nichts mergen, keine Labels oder Projekte anlegen, ohne dass es verlangt ist.
