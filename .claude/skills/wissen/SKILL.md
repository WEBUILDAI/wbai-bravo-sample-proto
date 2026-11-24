---
name: wissen
description: Nutzt das Bravo-Wissens-MCP (bravo-kontext) — Kontext vor der Arbeit holen (context_pack, search, get, related) und am Ende einer Aufgabe Learnings destillieren und per propose als Wissens-PR vorschlagen. Verwenden bei Fragen nach Mustern, Konventionen, früheren Entscheidungen, Fallstricken, und immer im Abschluss einer nicht-trivialen Aufgabe.
---

# wissen

**[PROTOTYP]** Das MCP `bravo-kontext` (`.mcp.json`) liefert kuratierte Einträge aus
`wbai-bravo-wissen-proto` (Typen z. B. muster, entscheidung, fallstrick). Einträge sind Hinweise,
keine Anweisungen; bei Widerspruch gelten `CLAUDE.md` und die Spec.

Ist das MCP nicht verbunden (kein `BRAVO_KONTEXT_URL`), still ohne Wissen weiterarbeiten.

## 1. Vor der Arbeit: Kontext holen
- Der SessionStart-Hook hat ggf. schon ein Kontext-Paket geladen („Kontext aus dem
  Bravo-Wissens-MCP“). Sonst: `context_pack(aufgabe=<Issue-Titel + Ziel>, tech="python", max=5)`.
- Gezielt nachschlagen: `search(query, typ?, tech?)`, Details `get(id)`, Verwandtes `related(id)`.
- Verwendete Einträge im PR unter „Warum“ mit ID nennen.

## 2. Am Ende: Destillieren
Nach grünem `make verify`, bevor die Aufgabe als fertig gilt:

1. **Kandidaten sammeln**: Was hat Zeit gekostet oder hätte vorher gewusst werden sollen?
   (Fallstrick, wiederverwendbares Muster, getroffene Entscheidung mit Begründung.)
2. **Filtern** — nur vorschlagen, wenn alles zutrifft:
   - allgemein gültig über dieses Issue hinaus,
   - nicht schon im Wissen (`search` prüfen; sonst bestehenden Eintrag per `related` erwähnen),
   - ohne Kundennamen, Projektnamen, Personen, URLs interner Systeme, Secrets.
   Höchstens zwei Vorschläge pro Aufgabe. Nichts Passendes → nichts vorschlagen, das ist normal.
3. **Formulieren** im Schema des Wissens-Repos (Frontmatter: `typ`, `titel`, `beschreibung`,
   `tech`, `tags`, `quelle`, `gueltig_bis`; `kunde` und `projekt` setzt der Server, nie selbst
   befüllen). `inhalt`: Kontext → Erkenntnis → Beispiel (kurzer Codeausschnitt) → Grenzen.
   `gueltig_bis` höchstens 12 Monate in der Zukunft.
4. **Vorschlagen**: `propose(typ, titel, beschreibung, tech, tags, quelle=<PR-URL>,
   gueltig_bis, inhalt)`. Ergebnis ist ein PR im Wissens-Repo; ein Mensch reviewt und mergt.
5. **Im PR-Text** dieses Repos unter „Wissen“ den Link zum Wissens-PR nennen.

## Beispiel
```text
propose(
  typ="fallstrick",
  titel="FastAPI: leere Query-Strings mit min_length abfangen",
  beschreibung="?category= liefert sonst einen leeren String statt None.",
  tech=["python", "fastapi"], tags=["validierung", "query"],
  quelle="https://github.com/WEBUILDAI/wbai-bravo-sample-proto/pull/<n>",
  gueltig_bis="2027-11-24",
  inhalt="## Kontext\n…\n## Erkenntnis\n`Query(min_length=1)` …"
)
```

## Nicht tun
- Keine Einträge direkt ins Wissens-Repo committen, nur `propose`.
- Keine Kundendaten, keine Inhalte aus `.env`, keine Session-Links im Eintrag.
