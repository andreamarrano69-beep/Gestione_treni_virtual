"""Indirizzi della finestra "Scegli linea": linee salvate, stazioni, destinazioni."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from treni.api import serializzazione as ser
from treni.fonti.base import ErroreFonte
from treni.linee.abbinamento import normalizza_nome
from treni.linee.caricatore import carica_linea
from treni.linee.salvataggio import elenco_linee, salva_linea
from treni.servizi.costruttore_linea import costruisci_linea
from treni.servizi.tratte import destinazioni

router = APIRouter(prefix="/api")


class RichiestaAttiva(BaseModel):
    id: str


class RichiestaCrea(BaseModel):
    codice: str  # stazione di partenza
    nome: str
    capolinea: str  # destinazione scelta


def _errore_fonte(e: ErroreFonte) -> HTTPException:
    return HTTPException(status_code=502, detail=str(e))


@router.get("/linee")
def linee(request: Request) -> dict:
    imp = request.app.state.impostazioni
    return {
        "attiva": request.app.state.gestore.aggiornatore.linea.id,
        "linee": elenco_linee(imp.cartella_linee),
    }


@router.post("/linee/attiva")
async def attiva(richiesta: RichiestaAttiva, request: Request) -> dict:
    imp = request.app.state.impostazioni
    if richiesta.id not in {l["id"] for l in elenco_linee(imp.cartella_linee)}:
        raise HTTPException(status_code=404, detail="Linea non trovata")
    linea = carica_linea(imp.cartella_linee, richiesta.id)
    await request.app.state.gestore.attiva(linea)
    return ser.linea_json(linea)


@router.get("/stazioni")
async def cerca_stazioni(testo: str, request: Request) -> list[dict]:
    if len(testo.strip()) < 2:
        return []
    try:
        trovate = await request.app.state.gestore.fonte.cerca_stazioni(testo.strip())
    except ErroreFonte as e:
        raise _errore_fonte(e) from e
    return [{"nome": nome, "codice": codice} for nome, codice in trovate[:30]]


@router.get("/stazioni/{codice}/destinazioni")
async def elenco_destinazioni(codice: str, nome: str, request: Request) -> list[dict]:
    try:
        trovate = await destinazioni(request.app.state.gestore.fonte, codice, nome)
    except ErroreFonte as e:
        raise _errore_fonte(e) from e
    return [{"capolinea": d.capolinea, "treni": len(d.voci), "categorie": d.categorie} for d in trovate]


@router.post("/linee/crea")
async def crea(richiesta: RichiestaCrea, request: Request) -> dict:
    gestore = request.app.state.gestore
    try:
        trovate = await destinazioni(gestore.fonte, richiesta.codice, richiesta.nome)
        scelta = next(
            (d for d in trovate if normalizza_nome(d.capolinea) == normalizza_nome(richiesta.capolinea)),
            None,
        )
        if scelta is None:
            raise HTTPException(status_code=404, detail="Nessun treno verso questa destinazione adesso")
        linea = await costruisci_linea(gestore.fonte, richiesta.codice, richiesta.nome, scelta.capolinea, scelta.voci)
    except ErroreFonte as e:
        raise _errore_fonte(e) from e
    salva_linea(request.app.state.impostazioni.cartella_linee, linea)
    await gestore.attiva(linea)
    return ser.linea_json(linea)
