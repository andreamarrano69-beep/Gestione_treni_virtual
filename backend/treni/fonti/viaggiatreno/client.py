"""Chiamate HTTP ai servizi (non ufficiali) di ViaggiaTreno.

Restituisce i dati così come arrivano; la conversione in oggetti del dominio
sta in parser.py.
"""

from datetime import datetime
from urllib.parse import quote
from zoneinfo import ZoneInfo

import httpx

from treni.fonti.base import ErroreFonte

ROMA = ZoneInfo("Europe/Rome")
_GIORNI = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_MESI = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def formato_data_vt(istante: datetime) -> str:
    """ViaggiaTreno vuole la data come la stampa JavaScript:
    'Wed Oct 29 2026 10:05:00 GMT+0100'."""
    d = istante.astimezone(ROMA)
    return (
        f"{_GIORNI[d.weekday()]} {_MESI[d.month - 1]} {d.day:02d} {d.year} "
        f"{d:%H:%M:%S} GMT{d:%z}"
    )


class ClientViaggiaTreno:
    def __init__(self, url_base: str, timeout_s: float = 15):
        self._url = url_base.rstrip("/")
        self._http = httpx.AsyncClient(
            timeout=timeout_s,
            headers={"User-Agent": "Mozilla/5.0 (GestioneTreniVirtual)"},
        )

    async def _get(self, percorso: str) -> httpx.Response:
        try:
            risposta = await self._http.get(f"{self._url}/{percorso}")
        except httpx.HTTPError as e:
            raise ErroreFonte(f"ViaggiaTreno non raggiungibile: {e}") from e
        if risposta.status_code >= 500:
            raise ErroreFonte(f"ViaggiaTreno ha risposto {risposta.status_code}")
        return risposta

    async def _json(self, percorso: str):
        risposta = await self._get(percorso)
        if risposta.status_code != 200 or not risposta.content.strip():
            return None
        try:
            return risposta.json()
        except ValueError:
            return None

    async def cerca_stazione(self, testo: str) -> list[tuple[str, str]]:
        """[(nome, codice)], es. [('MILANO CENTRALE', 'S01700'), ...]"""
        risposta = await self._get(f"autocompletaStazione/{quote(testo, safe='')}")
        risultati = []
        for riga in risposta.text.splitlines():
            if "|" in riga:
                nome, codice = riga.split("|", 1)
                risultati.append((nome.strip(), codice.strip()))
        return risultati

    async def partenze(self, codice_stazione: str, quando: datetime) -> list[dict]:
        data = quote(formato_data_vt(quando), safe="")
        return await self._json(f"partenze/{codice_stazione}/{data}") or []

    async def arrivi(self, codice_stazione: str, quando: datetime) -> list[dict]:
        data = quote(formato_data_vt(quando), safe="")
        return await self._json(f"arrivi/{codice_stazione}/{data}") or []

    async def andamento_treno(self, cod_origine: str, numero: str, data_ms: int) -> dict | None:
        return await self._json(f"andamentoTreno/{cod_origine}/{numero}/{data_ms}")

    async def chiudi(self) -> None:
        await self._http.aclose()
