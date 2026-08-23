from dataclasses import asdict
from .offer import BONGO_STARTER


CATALOG = {
    "bongo-starter": asdict(BONGO_STARTER),
}


def get_offer(offer_id: str):
    return CATALOG.get(offer_id)
