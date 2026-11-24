---
name: aenderung-vorschlagen
description: Hilft Fachanwender:innen in der Claude-App, eine Änderung am Bravo-Sample (wbai-bravo-sample-proto) als Vorschlag einzureichen, Rückfragen zu beantworten und den Status zu verfolgen, über die Tools des Wissens-MCP (vorschlag_anlegen, meine_rueckfragen, antworten, status). Verwenden bei „ich hätte gern …“, „kann die App …“, „Änderung vorschlagen“, „gibt es Rückfragen zu meinem Vorschlag?“, „was ist aus meinem Vorschlag geworden?“.
---

# aenderung-vorschlagen

**[PROTOTYP]** Weg eines Vorschlags:

```
Claude-App ─ vorschlag_anlegen ─► Issue mit Label `triage` ─► bravo-triage.yml
   ▲                                                            │
   └──── meine_rueckfragen / antworten ◄── Label `rueckfrage` ◄─┤
                                         Label `triage-ok` ◄────┘ ─► Mensch setzt `ready`
                                                                     ─► bravo-implement.yml ─► PR
```

## 1. Vorschlag aufnehmen
Im Gespräch klären, bevor etwas angelegt wird:
- **Was** soll anders sein (ein Satz, aus Sicht der Nutzer:innen)?
- **Warum** (Problem, Nutzen)?
- **Woran** erkennt man, dass es fertig ist? Mindestens ein Beispiel „Wenn … dann …“.
- **Was nicht** dazugehört.

Nicht nach technischen Details fragen, die die Person nicht wissen kann. Ein Vorschlag = eine
Änderung; mehrere Wünsche → mehrere Vorschläge.

Zusammenfassung zeigen und bestätigen lassen. Keine Kundennamen, Personendaten oder Secrets
übernehmen; falls genannt, neutral umformulieren und darauf hinweisen.

## 2. Anlegen
`vorschlag_anlegen(titel, was, warum, akzeptanz, nicht_ziele)`. Antwort: Issue-Nummer und Link.
Der Person sagen: Ein automatischer Triage-Lauf prüft den Vorschlag in wenigen Minuten und stellt
ggf. Rückfragen.

## 3. Rückfragen beantworten
- `meine_rueckfragen()` listet offene Rückfragen zu eigenen Vorschlägen.
- Jede Frage in Alltagssprache erklären, Antwort der Person sinngemäß übernehmen und
  `antworten(issue, text)` aufrufen. Die Antwort startet die Triage erneut.

## 4. Status
`status(issue)` und übersetzen:

| Label | Bedeutung für die Person |
|---|---|
| `triage` | eingegangen, wird geprüft |
| `rueckfrage` | wartet auf Antwort von dir |
| `triage-ok` | geprüft, wartet auf Freigabe durch das Team |
| `ready` | freigegeben, wird umgesetzt |
| PR verlinkt | Umsetzung liegt zur Prüfung vor |
| geschlossen | erledigt oder abgelehnt (Begründung im letzten Kommentar) |

## Grenzen
- Kein Versprechen zu Terminen oder Umsetzung; das Team entscheidet.
- Sind die Tools nicht verfügbar, den Vorschlag als Text formulieren, damit die Person ihn
  weitergeben kann.
