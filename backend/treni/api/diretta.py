"""Canale WebSocket: invia allo schermo lo stato della circolazione ogni pochi secondi."""

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from treni.api import serializzazione as ser
from treni.api.rotte import scatta

router = APIRouter()


@router.websocket("/ws")
async def diretta(websocket: WebSocket) -> None:
    await websocket.accept()
    app = websocket.app
    intervallo = app.state.impostazioni.intervallo_diffusione_s
    try:
        while True:
            ist = scatta(websocket)
            await websocket.send_json(ser.istantanea_json(ist, app.state.gestore.aggiornatore.stato_fonte))
            await asyncio.sleep(intervallo)
    except WebSocketDisconnect:
        pass
