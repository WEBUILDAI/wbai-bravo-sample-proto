# 0002 Item per ID abrufen

- Status: entwurf (Beispiel-Spec für `plan-to-issues` und den Async-Loop)
- Board: wird per Skill `plan-to-issues` bzw. vom Operator angelegt

## Ziel
Clients können ein einzelnes Item direkt über seine ID laden.

## Verhalten
- `GET /items/{item_id}` mit ganzzahliger `item_id` liefert das Item (`id`, `name`, `category`).
- Unbekannte ID: `404` mit `{"detail": "Item <id> nicht gefunden"}`.
- Nicht-ganzzahlige ID (z. B. `/items/abc`): `422` (FastAPI-Validierung).
- Negative IDs oder `0`: `422` (`item_id >= 1`).
- Jeder Abruf erzeugt eine Log-Zeile auf INFO mit der ID, ein 404 auf WARNING.
- `GET /items?category=` (Spec 0001) bleibt unverändert.

## Akzeptanzkriterien
1. Given Items 1–3, when `GET /items/3`, then `200` und `{"id": 3, "name": "Akkuschrauber",
   "category": "werkzeug"}`.
2. Given Items 1–3, when `GET /items/99`, then `404` und `detail` nennt die ID.
3. Given Items 1–3, when `GET /items/abc`, then `422`.
4. Given Items 1–3, when `GET /items/0`, then `422`.
5. Given ein 404, when Logs geprüft werden, then genau eine WARNING-Zeile mit der ID.

## Slices (Vorschlag)
- Slice 1: Endpunkt, Kriterien 1–3, Tests.
- Slice 2: Untergrenze `>= 1`, Logging, Kriterien 4–5, Tests mit `caplog`.

## Nicht-Ziele
- Ändern oder Löschen von Items, Persistenz, Auth.
