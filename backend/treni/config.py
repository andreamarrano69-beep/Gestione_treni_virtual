"""Impostazioni dell'applicazione, lette dalle variabili d'ambiente."""

import os
from dataclasses import dataclass
from pathlib import Path

CARTELLA_BACKEND = Path(__file__).resolve().parent.parent
CARTELLA_PROGETTO = CARTELLA_BACKEND.parent


@dataclass(frozen=True)
class Impostazioni:
    fonte: str  # "viaggiatreno" oppure "demo"
    linea: str  # nome del file in dati/linee (senza .yaml)
    cartella_linee: Path
    cartella_cache: Path
    cartella_frontend: Path
    url_viaggiatreno: str
    intervallo_scoperta_s: int  # ogni quanto cercare nuovi treni nelle stazioni
    intervallo_andamento_s: int  # ogni quanto aggiornare i treni già noti
    intervallo_diffusione_s: float  # ogni quanto inviare lo stato allo schermo
    richieste_parallele: int
    orizzonte_incroci_min: int
    host: str
    porta: int


def _intero(nome: str, predefinito: int) -> int:
    return int(os.environ.get(nome, predefinito))


def carica_impostazioni() -> Impostazioni:
    return Impostazioni(
        fonte=os.environ.get("TRENI_FONTE", "viaggiatreno"),
        linea=os.environ.get("TRENI_LINEA", "milano_bologna"),
        cartella_linee=CARTELLA_PROGETTO / "dati" / "linee",
        cartella_cache=CARTELLA_PROGETTO / "dati" / "cache",
        cartella_frontend=CARTELLA_PROGETTO / "frontend",
        url_viaggiatreno=os.environ.get(
            "TRENI_URL_VIAGGIATRENO",
            "http://www.viaggiatreno.it/infomobilita/resteasy/viaggiatreno",
        ),
        intervallo_scoperta_s=_intero("TRENI_INTERVALLO_SCOPERTA", 300),
        intervallo_andamento_s=_intero("TRENI_INTERVALLO_ANDAMENTO", 60),
        intervallo_diffusione_s=float(os.environ.get("TRENI_INTERVALLO_DIFFUSIONE", 2)),
        richieste_parallele=_intero("TRENI_RICHIESTE_PARALLELE", 4),
        orizzonte_incroci_min=_intero("TRENI_ORIZZONTE_INCROCI", 30),
        host=os.environ.get("TRENI_HOST", "127.0.0.1"),
        porta=_intero("TRENI_PORTA", 8000),
    )
