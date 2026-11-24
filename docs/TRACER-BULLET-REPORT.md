# Tracer-Bullet-Report: wbai-bravo-sample-proto

**[PROTOTYP, nonprod]** Stand 2026-11-24, unbeaufsichtigter Lauf. Annahmen: `docs/ASSUMPTIONS.md`
(#7–#40 aus diesem Lauf).

## Slice-Status
| Slice | PR | Branch | Code/Doku | Blockiert durch Admin-Schritt |
|---|---|---|---|---|
| S1 Rest | #2 | `feature/s1-rest` | grün | Branch-Schutz auf `main` |
| S2 Async-Loop | #3 | `feature/s2-async-loop` | grün (`GET /items?category=` + 4 Tests) | Labels `board`/`slice`, Board-Issue + 2 Sub-Issues |
| S3 Teams-Hinweis | #4 | `feature/s3-teams-card-test` | grün (6 Payload-Tests) | Teams-Webhook bzw. Relay (S6) für echten Versand |
| S4 Sync nach ADO | #5 | `feature/s4-sync-ado` | grün (Skript gegen Bare-Repo getestet) | Entra-App + Federated Credential, ADO-Projekt/-Repo, SP-Rechte, 6 Repo-Variablen |
| S7 Kontext in Sessions | #6 | `feature/s7-kontext-in-sessions` | grün (Hook gegen Fake-MCP getestet) | Deploy Kontext-Server (S5/S6), `BRAVO_KONTEXT_URL`/Token im Cloud environment |
| S8 Auto-Claude | #7 | `feature/s8-auto-claude` | grün (Gerüst, Strukturtests) | – (Start nur auf ausdrücklichen Wunsch) |
| S9 Vorschläge (sample) | #8 | `feature/s9-vorschlaege` | grün (Guard-Tests) | WIF-Regel A14 + Repo-Variablen, Labels, S9-Tools + App im Kontext-Repo |
| S10 Automatische Läufe (sample) | #9 | `feature/s10-automatische-laeufe` | grün (Guard-/Grenzen-Tests) | WIF-Regel A14, Labels, GitHub App A12 als PR-Token |

„grün“ heißt: `make verify` lokal grün und CI-Check `verify` am PR. Kein Workflow mit
Azure-/Anthropic-Zugriff ist bisher echt gelaufen; ohne Variablen enden sie als grüner No-op.

Nicht in diesem Repo: S5, S6, S9-Tools (kontext/wissen), `bravo-wissen-pflege.yml` (wissen).

## Merge-Reihenfolge
Die Branches sind gestapelt (ADR 0002, ASSUMPTIONS #8). Gemerged wird in dieser Reihenfolge:
#2 → #3 → #4 → #5 → #6 → #7 → #8 → #9 → Report-PR. Nach jedem Merge zeigt der nächste PR nur
seinen eigenen Diff, bei Squash-Merge eventuell erst nach „Update branch“. Gemerged wird nur von
einem Menschen.

## Offene Admin-Schritte (lokal, nicht aus der Cloud session)
### GitHub (Repo-Admin)
1. Branch-Schutz `main`: `docs/branch-protection.md`, danach Test-PR mit absichtlich rotem Test.
2. Labels anlegen:
   ```bash
   for l in board slice triage rueckfrage triage-ok ready in-review; do
     gh label create "$l" -R WEBUILDAI/wbai-bravo-sample-proto --force; done
   ```
3. Repo-Variablen S4: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`,
   `ADO_ORG_URL`, `ADO_PROJECT`, `ADO_REPO` (`docs/output-sync.md`).
4. Repo-Variablen S9/S10: `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID` (WIF A14).
5. GitHub App A12 (`wbai-bravo-mcp-proto`) installieren; optional als Token für
   `bravo-implement`, damit CI auf Agent-PRs startet (ASSUMPTIONS #38).
6. Board-Issue „Items nach Kategorie filtern“ (Spec 0001) mit 2 Slice-Sub-Issues anlegen.

### Entra / Azure DevOps
7. Entra-App `wbai-bravo-sample-sync-proto`, SP, Federated Credential
   `repo:WEBUILDAI/wbai-bravo-sample-proto:ref:refs/heads/main`.
8. ADO-Projekt und -Repo mit initialem `main`; SP als Benutzer (Basic) mit Contribute,
   Create branch, Contribute to pull requests.

### Cloud environment / Teams
9. Setup-Skript `bash scripts/setup.sh` im Cloud environment eintragen. Der SessionStart-Hook
   zieht `.venv` notfalls nach.
10. `BRAVO_KONTEXT_URL` als Env und Bearer-Token als Network secret, sobald S6 deployt ist.
11. Teams-Webhook im Kontext-Server hinterlegen (S6).

## Nächste Befehle
```bash
# Review und Merge in Reihenfolge
gh pr list -R WEBUILDAI/wbai-bravo-sample-proto
gh pr checks 2 -R WEBUILDAI/wbai-bravo-sample-proto

# Nach Merge von S4 + Variablen: Sync testen
gh workflow run sync-ado -R WEBUILDAI/wbai-bravo-sample-proto --ref main

# Async-Loop end-to-end
claude --cloud "Board #<n> umsetzen"

# S9/S10 nach WIF-Einrichtung: Testvorschlag
gh issue create -R WEBUILDAI/wbai-bravo-sample-proto -t "Test: Item per ID" \
  -b "Bitte Spec docs/specs/0002-items-by-id.md umsetzen." -l triage
# danach Label ready setzen → bravo-implement
```

## Zu prüfen beim ersten echten Lauf
- `az repos pr create` mit Entra-Token ohne PAT (ASSUMPTIONS #17).
- Eingaben `anthropic_federation_rule_id` / `anthropic_organization_id` der Action (#33).
- Branch-Logik der Action im Automationsmodus (#36), `author_association` bei privater
  Org-Mitgliedschaft (#32).
- MCP-Pfad `/mcp` und `/notify` des Kontext-Servers (#21).
