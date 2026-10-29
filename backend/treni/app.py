"""Costruisce l'applicazione web: API, canale in diretta e pagine dello schermo."""

from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from treni.api import diretta, rotte
from treni.config import Impostazioni, carica_impostazioni
from treni.fonti.base import FonteDati
from treni.linee.caricatore import carica_linea
from treni.servizi.aggiornatore import Aggiornatore
from treni.servizi.istantanea import Fotografo


def crea_fonte(imp: Impostazioni) -> FonteDati:
    if imp.fonte == "demo":
        from treni.fonti.demo.fonte import FonteDemo

        return FonteDemo()
    if imp.fonte == "viaggiatreno":
        from treni.fonti.viaggiatreno.fonte import FonteViaggiaTreno

        return FonteViaggiaTreno(imp.url_viaggiatreno, imp.cartella_cache)
    raise ValueError(f"Fonte sconosciuta: {imp.fonte} (usa 'viaggiatreno' o 'demo')")


def crea_app(imp: Impostazioni | None = None) -> FastAPI:
    imp = imp or carica_impostazioni()

    @asynccontextmanager
    async def ciclo_di_vita(app: FastAPI):
        linea = carica_linea(imp.cartella_linee, imp.linea)
        aggiornatore = Aggiornatore(crea_fonte(imp), linea, imp)
        app.state.impostazioni = imp
        app.state.aggiornatore = aggiornatore
        app.state.fotografo = Fotografo(timedelta(minutes=imp.orizzonte_incroci_min))
        aggiornatore.avvia()
        yield
        await aggiornatore.ferma()

    app = FastAPI(title="Gestione Treni Virtual", lifespan=ciclo_di_vita)
    app.include_router(rotte.router)
    app.include_router(diretta.router)
    app.mount("/", StaticFiles(directory=imp.cartella_frontend, html=True), name="schermo")
    return app
