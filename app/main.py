"""FastAPI-Anwendung mit Health-Check und einer kleinen Item-Liste."""

import logging

from fastapi import FastAPI
from pydantic import BaseModel

from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="wbai-bravo-sample-proto", version="0.1.0")


class Item(BaseModel):
    """Ein Eintrag der Beispiel-Liste.

    Attributes:
        id: Eindeutige ID.
        name: Anzeigename.
        category: Kategorie für spätere Filter.
    """

    id: int
    name: str
    category: str


ITEMS: list[Item] = [
    Item(id=1, name="Schraube", category="bauteil"),
    Item(id=2, name="Mutter", category="bauteil"),
    Item(id=3, name="Akkuschrauber", category="werkzeug"),
]


@app.get("/health")
def health() -> dict[str, str]:
    """Liefert den Status des Service.

    Returns:
        Statusobjekt mit dem Feld "status".
    """
    return {"status": "ok"}


@app.get("/items")
def list_items() -> list[Item]:
    """Liefert alle Items.

    Returns:
        Liste aller Items.
    """
    logger.info("Liste %d Items", len(ITEMS))
    return ITEMS
