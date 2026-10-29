"""Indirizzi HTTP letti dallo schermo: linea, stato attuale, dettaglio treno."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from treni.api import serializzazione as ser

router = APIRouter(prefix="/api")


def scatta(request: Request):
    """Fotografia della circolazione in questo istante."""
    gestore = request.app.state.gestore
    agg, fotografo = gestore.aggiornatore, gestore.fotografo
    adesso = datetime.now(timezone.utc)
    treni = list(agg.registro.treni.values())
    return fotografo.scatta(agg.linea, agg.calcolatore, treni, adesso)


@router.get("/linea")
def linea(request: Request) -> dict:
    return ser.linea_json(request.app.state.gestore.aggiornatore.linea)


@router.get("/stato")
def stato(request: Request) -> dict:
    return ser.istantanea_json(scatta(request), request.app.state.gestore.aggiornatore.stato_fonte)


@router.get("/treni/{chiave}")
def dettaglio_treno(chiave: str, request: Request) -> dict:
    agg = request.app.state.gestore.aggiornatore
    ist = scatta(request)
    for t in ist.treni:
        if t.treno.chiave == chiave:
            return ser.dettaglio_treno_json(t, ist.adesso, agg.calcolatore.stazioni_di(t.treno))
    raise HTTPException(status_code=404, detail="Treno non seguito")
