"""Fonte dati reale: i treni in circolazione secondo ViaggiaTreno."""

import logging
from datetime import datetime, timezone
from pathlib import Path

from treni.dominio.linea import Linea
from treni.dominio.treno import RiferimentoTreno, Treno
from treni.fonti.base import ErroreFonte
from treni.fonti.viaggiatreno import parser
from treni.fonti.viaggiatreno.client import ClientViaggiaTreno
from treni.fonti.viaggiatreno.codici import risolvi_codici

log = logging.getLogger(__name__)


class FonteViaggiaTreno:
    nome = "ViaggiaTreno"
    in_tempo_reale = True

    def __init__(self, url_base: str, cartella_cache: Path):
        self._client = ClientViaggiaTreno(url_base)
        self._cartella_cache = cartella_cache

    async def prepara(self, linea: Linea) -> Linea:
        linea = await risolvi_codici(linea, self._client, self._cartella_cache)
        mancanti = [s.nome for s in linea.stazioni if not s.codice]
        if len(mancanti) == len(linea.stazioni):
            raise ErroreFonte("Nessun codice stazione trovato: ViaggiaTreno è raggiungibile?")
        if mancanti:
            log.warning("Stazioni senza codice (non usate per cercare treni): %s", mancanti)
        return linea

    async def scopri_treni(self, linea: Linea) -> list[RiferimentoTreno]:
        adesso = datetime.now(timezone.utc)
        trovati: dict[str, RiferimentoTreno] = {}
        errori = 0
        for stazione in linea.stazioni:
            if not stazione.codice:
                continue
            try:
                voci = await self._client.partenze(stazione.codice, adesso)
                voci += await self._client.arrivi(stazione.codice, adesso)
            except ErroreFonte as e:
                errori += 1
                log.warning("Tabellone di %s non disponibile: %s", stazione.nome, e)
                continue
            for voce in voci:
                rif = parser.riferimento_da_tabellone(voce)
                if rif:
                    trovati[rif.chiave] = rif
        if errori and not trovati:
            raise ErroreFonte("Nessun tabellone di stazione disponibile")
        return list(trovati.values())

    async def andamento(self, riferimento: RiferimentoTreno) -> Treno | None:
        dati = await self._client.andamento_treno(
            riferimento.cod_origine, riferimento.numero, riferimento.data_partenza_ms
        )
        if not dati or not dati.get("fermate"):
            return None
        return parser.treno_da_andamento(dati, riferimento)

    async def chiudi(self) -> None:
        await self._client.chiudi()
