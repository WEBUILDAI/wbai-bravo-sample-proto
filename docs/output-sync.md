# Output-Sync nach Azure DevOps (S4)

**[PROTOTYP, nonprod]** GitHub bleibt Arbeitsort für Sessions und Agenten. Der Kunde bekommt den
Stand von `main` als PR in seinem Azure-DevOps-Repo und mergt dort selbst.

## Ablauf
1. Push auf `main` (also nach jedem Merge) startet `.github/workflows/sync-ado.yml`.
2. `azure/login@v2` meldet sich per OIDC an (kein Secret). Entra-App
   `wbai-bravo-sample-sync-proto`, Federated Credential mit Subject
   `repo:WEBUILDAI/wbai-bravo-sample-proto:ref:refs/heads/main`.
3. Der Workflow holt ein Access-Token für Azure DevOps (Resource
   `499b84ac-1321-427f-aa17-267ca6975798`) und maskiert es im Log.
4. `scripts/sync-ado.sh` klont ADO-`main`, ersetzt den Inhalt durch den committeten Stand von
   GitHub (ohne Exclude-Pfade) und pusht `sync/<short-sha>`. Ist nichts anders, passiert nichts.
5. `az repos pr create` öffnet den PR `[PROTOTYP] Sync <short-sha>` gegen ADO-`main`.

Der ADO-Branch enthält einen einzigen Commit pro Sync, nicht die GitHub-Historie. Damit landen
auch ausgeschlossene Dateien nicht über alte Commits im Kunden-Repo.

## Repo-Variablen (Settings → Secrets and variables → Actions → Variables)
| Variable | Beispiel |
|---|---|
| `AZURE_CLIENT_ID` | Client-ID der App `wbai-bravo-sample-sync-proto` |
| `AZURE_TENANT_ID` | Tenant-ID WE BUILD AI |
| `AZURE_SUBSCRIPTION_ID` | Sponsorship-Subscription |
| `ADO_ORG_URL` | `https://dev.azure.com/<org>` |
| `ADO_PROJECT` | `wbai-bravo-proto` |
| `ADO_REPO` | `wbai-bravo-sample-proto` |

Fehlt eine Variable, läuft der Workflow grün durch und schreibt eine Notice mit den fehlenden Namen.

## Exclude-Liste
`.github/ado-sync-exclude.txt`, eine Zeile pro Pfad (git-Pathspec). Im Prototyp leer.
Empfohlener Kunden-Default: `.claude/`, `CLAUDE.md`, `.mcp.json` (Agent-Konfiguration bleibt bei uns).

## Einrichtung (lokal, Admin)
```bash
# 1. Entra-App + Service Principal
az ad app create --display-name wbai-bravo-sample-sync-proto
appId=$(az ad app list --display-name wbai-bravo-sample-sync-proto --query '[0].appId' -o tsv)
az ad sp create --id "$appId"

# 2. Federated Credential für main
az ad app federated-credential create --id "$appId" --parameters '{
  "name": "github-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:WEBUILDAI/wbai-bravo-sample-proto:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'

# 3. Azure DevOps: SP als Benutzer ins Projekt aufnehmen (Organization settings → Users,
#    Access level Basic), im Ziel-Repo Rechte "Contribute" und "Create branch" und
#    "Contribute to pull requests". Ziel-Repo mit initialem main (README) anlegen.

# 4. Repo-Variablen
gh variable set AZURE_CLIENT_ID --body "$appId"
gh variable set AZURE_TENANT_ID --body "<tenant>"
gh variable set AZURE_SUBSCRIPTION_ID --body "<subscription>"
gh variable set ADO_ORG_URL --body "https://dev.azure.com/<org>"
gh variable set ADO_PROJECT --body "<projekt>"
gh variable set ADO_REPO --body "wbai-bravo-sample-proto"
```
`azure/login` braucht eine Subscription; der SP benötigt dort keine Rolle (nur Login, keine
Ressourcen). Falls die Organisation das verlangt, `Reader` auf `rg-wbai-bravo-proto` genügt.

## Prüfen
- Actions → `sync-ado` → „Run workflow“ (workflow_dispatch läuft ebenfalls nur auf `main`, weil
  das Federated Credential nur `refs/heads/main` erlaubt).
- In ADO: Branch `sync/<short-sha>` und PR vorhanden.
- Lokal ohne Azure: `pytest tests/test_sync_ado.py` (Bare-Repo als ADO-Ersatz).
