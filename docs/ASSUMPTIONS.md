# Annahmen

| # | Annahme | Grund | Offen? |
|---|---|---|---|
| 1 | Repos sind public. | GitHub Free: Branch-Schutz nur für public Repos. Freigabe Lukas, solange keine Credentials sichtbar sind. | nein |
| 2 | PRs gehen direkt auf `main`, kein `develop`. | Prototyp, schneller Durchstich. Abweichung vom WBAI-Standard. | nein |
| 3 | Setup-PRs des Operators werden nach grüner CI vom Operator gemerged; PRs aus Cloud sessions, Bots und Wissens-PRs nie automatisch. | Mensch bleibt Gate für Agent-Output. | nein |
| 4 | Stop-Hook blockiert nur einmal (`stop_hook_active`), danach meldet er nur. | Keine Endlosschleife. | nein |
| 5 | Teams-Hinweis nur in Cloud sessions (`CLAUDE_CODE_REMOTE=true`) oder mit `BRAVO_NOTIFY=always`. | Lokal kein Lärm. | nein |
| 6 | In Cloud sessions geht der Teams-Hinweis über `BRAVO_KONTEXT_URL/notify`; der Webhook liegt nur im Kontext-Server. | Webhook-URL ist ein Secret und soll nicht in jede Session. | ja, S6 |
| 7 | Commits des unbeaufsichtigten Tracer-Bullet-Laufs tragen die neutrale Identität `wbai-bravo-proto <wbai-bravo-proto@users.noreply.github.com>`. | Keine Hinweise auf Werkzeuge, keine persönliche Adresse als Autor eines Agent-Laufs. | nein |
| 8 | Slice-Branches sind gestapelt: `feature/s2-…` basiert auf `feature/s1-…` usw.; jeder PR zielt auf `main`. Merge-Reihenfolge S1 → S2 → S3 → S4 → S7 → S8 → S9 → S10. | Alle Slices ergänzen `docs/ASSUMPTIONS.md` und teils dieselben Dateien; unabhängige Branches würden bei jedem Merge Konflikte erzeugen. Nach dem Merge eines PRs schrumpft der Diff des nächsten. Siehe `docs/decisions/0002-gestapelte-slice-branches.md`. | nein |
| 9 | S1-Rest: `docs/ASSUMPTIONS.md`, `docs/specs/` und `docs/decisions/0001-prototyp-rahmen.md` liegen bereits auf `main`. Der S1-PR ergänzt nur Entscheidungs-Index, ADR 0002 und die Anleitung für den Branch-Schutz. | Bestand nicht doppelt anlegen. | nein |
| 10 | Branch-Schutz auf `main` (Check `verify`, PR Pflicht) setzt ein Repo-Admin lokal (`docs/branch-protection.md`). | Die Cloud session hat keine Admin-Rechte auf Repo-Einstellungen. | ja, Admin |
| 11 | `GET /items?category=` vergleicht exakt (Groß-/Kleinschreibung zählt), unbekannte Kategorie → `200 []`, leerer Wert → `422`. | Spec 0001; leerer Filter ist eher ein Client-Fehler als „alle“. | nein |
| 12 | Issue-Templates setzen Labels `board` und `slice`; die Labels legt der Operator an, falls GitHub sie nicht automatisch erzeugt. | Templates können Labels nur zuweisen, wenn sie existieren. | ja, Admin |
| 13 | Board-Issue „Items nach Kategorie filtern“ mit zwei Slice-Sub-Issues legt der lokale Operator an; die Implementierung liegt bereits im S2-PR. | HANDOFF: Board-Issues nicht aus der Cloud session. Das Board dokumentiert dann den bereits umgesetzten Stand bzw. dient als Probelauf für `claude --cloud`. | ja, Operator |
| 14 | Der Card-Payload wird über das echte Skript getestet; `curl` ersetzt ein Fake im `PATH`. Neue Variable `BRAVO_ENV_FILE` lenkt die `.env` um, damit lokale Werte Tests nicht beeinflussen. | Kein Refactoring des Skripts nötig, Test deckt auch Ziel-URL und Header ab. | nein |
