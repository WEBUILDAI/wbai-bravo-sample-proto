# Branch-Schutz für `main` (Admin-Schritt)

Die Cloud session hat keine Admin-Rechte. Ein Repo-Admin führt lokal aus:

```bash
gh api -X PUT repos/WEBUILDAI/wbai-bravo-sample-proto/branches/main/protection \
  -H "Accept: application/vnd.github+json" --input - <<'JSON'
{
  "required_status_checks": {"strict": true, "contexts": ["verify"]},
  "enforce_admins": false,
  "required_pull_request_reviews": {"required_approving_review_count": 0},
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
```

- `contexts: ["verify"]` ist der Job-Name aus `.github/workflows/ci.yml`.
- `required_approving_review_count: 0`: PR ist Pflicht, die Freigabe gibt der Operator beim
  Mergen (Prototyp, eine Person). Für Kunden auf mindestens 1 setzen.
- `enforce_admins: false`: Der Operator darf Setup-PRs selbst mergen (ASSUMPTIONS #3).

Prüfen:

```bash
gh api repos/WEBUILDAI/wbai-bravo-sample-proto/branches/main/protection \
  --jq '{checks: .required_status_checks.contexts, pr: (.required_pull_request_reviews != null)}'
```

Test: einen PR mit absichtlich rotem Test öffnen; der Merge-Button muss gesperrt sein.
