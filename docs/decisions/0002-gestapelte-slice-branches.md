# 0002 Gestapelte Slice-Branches

- Status: vorgeschlagen
- Datum: 2026-11-24

## Kontext
Der Tracer Bullet liefert acht Slices aus einem unbeaufsichtigten Lauf, je Slice ein PR gegen
`main`. Jeder Slice ergänzt `docs/ASSUMPTIONS.md`; S7 ändert `.claude/settings.json`, S9 und S10
bauen auf denselben Konventionen auf. Unabhängige Branches ab `main` würden beim Mergen
fortlaufend Konflikte erzeugen, die niemand im Lauf auflösen kann.

## Entscheidung
Die Slice-Branches bauen aufeinander auf (`feature/s1-rest` ← `feature/s2-async-loop` ← … ←
`feature/s10-automatische-laeufe`). Jeder PR zielt auf `main`, damit CI und Branch-Schutz greifen.
Gemerged wird in Slice-Reihenfolge. Nach jedem Merge zeigt der nächste PR nur noch seinen eigenen
Diff (bei Squash-Merge ggf. einmal „Update branch“ klicken).

## Folgen
- Review in Reihenfolge; wird ein früher Slice abgelehnt, muss der Rest neu gestapelt werden.
- Jeder PR nennt in der Beschreibung, auf welchem Branch er aufbaut.
- Für reguläre Arbeit (ein Issue, ein Slice) gilt weiter: Branch ab `main`.
