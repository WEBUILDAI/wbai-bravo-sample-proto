# 0001 Items nach Kategorie filtern

- Status: umgesetzt
- Board: wird vom Operator angelegt (siehe `docs/RUNBOOK.md`)

## Ziel
Clients können die Item-Liste auf eine Kategorie einschränken, ohne alle Items zu laden.

## Verhalten
- `GET /items` ohne Parameter liefert wie bisher alle Items.
- `GET /items?category=<kategorie>` liefert nur Items, deren `category` exakt gleich ist
  (Groß-/Kleinschreibung zählt).
- Unbekannte Kategorie: `200` mit leerer Liste `[]`, kein `404`.
- Leerer Wert (`?category=`): `422`, weil eine leere Kategorie kein sinnvoller Filter ist.
- Die Reihenfolge entspricht der ungefilterten Liste.

## Akzeptanzkriterien
1. Given drei Items (2× `bauteil`, 1× `werkzeug`), when `GET /items?category=bauteil`,
   then zwei Items, alle mit `category == "bauteil"`.
2. Given dieselben Items, when `GET /items?category=gibtsnicht`, then `200` und `[]`.
3. Given dieselben Items, when `GET /items`, then alle drei Items.
4. Given dieselben Items, when `GET /items?category=`, then `422`.

## Slices
- Slice 1: Query-Parameter und Filter in `app/main.py`, Tests 1–3.
- Slice 2: Validierung des leeren Werts, Test 4, OpenAPI-Beschreibung.

## Nicht-Ziele
- Mehrere Kategorien gleichzeitig, Teiltreffer, Groß-/Kleinschreibung ignorieren.
- Paginierung.
