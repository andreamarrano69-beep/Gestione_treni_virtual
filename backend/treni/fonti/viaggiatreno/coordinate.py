"""Coordinate geografiche delle stazioni, con cache su file."""

import json
from pathlib import Path

from treni.fonti.base import ErroreFonte
from treni.fonti.viaggiatreno.client import ClientViaggiaTreno


class CoordinateStazioni:
    def __init__(self, client: ClientViaggiaTreno, cartella_cache: Path):
        self._client = client
        self._percorso = cartella_cache / "coordinate_stazioni.json"
        self._cache: dict[str, list[float] | None] | None = None

    def _leggi(self) -> dict:
        if self._cache is None:
            esiste = self._percorso.exists()
            self._cache = json.loads(self._percorso.read_text(encoding="utf-8")) if esiste else {}
        return self._cache

    def _scrivi(self) -> None:
        self._percorso.parent.mkdir(parents=True, exist_ok=True)
        self._percorso.write_text(json.dumps(self._cache, indent=1), encoding="utf-8")

    async def di(self, codice: str) -> tuple[float, float] | None:
        cache = self._leggi()
        if codice not in cache:
            cache[codice] = await self._scarica(codice)
            self._scrivi()
        valore = cache[codice]
        return (valore[0], valore[1]) if valore else None

    async def _scarica(self, codice: str) -> list[float] | None:
        try:
            regione = await self._client.regione(codice)
            dati = await self._client.dettaglio_stazione(codice, regione) if regione else None
        except ErroreFonte:
            return None
        if not dati or not dati.get("lat") or not dati.get("lon"):
            return None
        return [float(dati["lat"]), float(dati["lon"])]
