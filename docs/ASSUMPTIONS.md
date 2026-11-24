# Annahmen

| # | Annahme | Grund | Offen? |
|---|---|---|---|
| 1 | Repos sind public. | GitHub Free: Branch-Schutz nur für public Repos. Freigabe Lukas, solange keine Credentials sichtbar sind. | nein |
| 2 | PRs gehen direkt auf `main`, kein `develop`. | Prototyp, schneller Durchstich. Abweichung vom WBAI-Standard. | nein |
| 3 | Setup-PRs des Operators werden nach grüner CI vom Operator gemerged; PRs aus Cloud sessions, Bots und Wissens-PRs nie automatisch. | Mensch bleibt Gate für Agent-Output. | nein |
| 4 | Stop-Hook blockiert nur einmal (`stop_hook_active`), danach meldet er nur. | Keine Endlosschleife. | nein |
| 5 | Teams-Hinweis nur in Cloud sessions (`CLAUDE_CODE_REMOTE=true`) oder mit `BRAVO_NOTIFY=always`. | Lokal kein Lärm. | nein |
| 6 | In Cloud sessions geht der Teams-Hinweis über `BRAVO_KONTEXT_URL/notify`; der Webhook liegt nur im Kontext-Server. | Webhook-URL ist ein Secret und soll nicht in jede Session. | ja, S6 |
