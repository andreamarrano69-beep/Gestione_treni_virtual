"""Cicli in background che interrogano la fonte e tengono aggiornato il registro."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from treni.config import Impostazioni
from treni.dominio.linea import Linea
from treni.dominio.treno import RiferimentoTreno, Treno
from treni.fonti.base import ErroreFonte, FonteDati
from treni.servizi.orario_stimato import stima_orario
from treni.servizi.posizione import CalcolatorePosizione
from treni.servizi.registro import RegistroTreni, StatoFonte

log = logging.getLogger(__name__)

MARGINE_DOPO_ARRIVO = timedelta(minutes=10)


class Aggiornatore:
    def __init__(self, fonte: FonteDati, linea: Linea, impostazioni: Impostazioni):
        self.fonte = fonte
        self.linea = linea
        self.calcolatore = CalcolatorePosizione(linea)
        self.registro = RegistroTreni()
        self.stato_fonte = StatoFonte(nome=fonte.nome, in_tempo_reale=fonte.in_tempo_reale)
        self._imp = impostazioni
        self._pronta = False
        self._limite = asyncio.Semaphore(impostazioni.richieste_parallele)
        self._compiti: list[asyncio.Task] = []

    def avvia(self) -> None:
        self._compiti = [
            asyncio.create_task(self._ciclo(self._scopri, self._imp.intervallo_scoperta_s)),
            asyncio.create_task(self._ciclo(self._aggiorna_noti, self._imp.intervallo_andamento_s)),
        ]

    async def ferma(self) -> None:
        for compito in self._compiti:
            compito.cancel()
        await asyncio.gather(*self._compiti, return_exceptions=True)
        await self.fonte.chiudi()

    async def _ciclo(self, azione, intervallo_s: int) -> None:
        while True:
            try:
                await azione()
            except ErroreFonte as e:
                self._segnala_errore(str(e))
            except Exception:  # un errore imprevisto non deve fermare il quadro
                log.exception("Errore durante l'aggiornamento")
                self._segnala_errore("Errore interno, vedi il log")
            await asyncio.sleep(intervallo_s)

    def _segnala_errore(self, messaggio: str) -> None:
        log.warning(messaggio)
        self.stato_fonte.ok = False
        self.stato_fonte.messaggio = messaggio

    async def _prepara(self) -> None:
        if not self._pronta:
            self.linea = await self.fonte.prepara(self.linea)
            self.calcolatore = CalcolatorePosizione(self.linea)
            self._pronta = True

    async def _scopri(self) -> None:
        await self._prepara()
        adesso = datetime.now(timezone.utc)
        riferimenti = await self.fonte.scopri_treni(self.linea)
        nuovi = [
            r for r in riferimenti
            if r.chiave not in self.registro.treni and not self.registro.e_ignorato(r.chiave, adesso)
        ]
        log.info("Scoperta: %d treni nei tabelloni, %d nuovi", len(riferimenti), len(nuovi))
        await self._scarica(nuovi)

    async def _aggiorna_noti(self) -> None:
        if self._pronta:
            await self._scarica([t.riferimento for t in self.registro.treni.values()])

    async def _scarica(self, riferimenti: list[RiferimentoTreno]) -> None:
        risultati = await asyncio.gather(*(self._andamento(r) for r in riferimenti))
        adesso = datetime.now(timezone.utc)
        for rif, treno in zip(riferimenti, risultati):
            if treno is None or treno.soppresso or not self.calcolatore.percorre_la_linea(treno):
                self.registro.ignora(rif.chiave, adesso)
            elif self._concluso(treno, adesso):
                self.registro.ignora(rif.chiave, adesso)
            else:
                self.registro.treni[rif.chiave] = treno
        self.stato_fonte.ok = True
        self.stato_fonte.messaggio = f"{len(self.registro.treni)} treni seguiti"
        self.stato_fonte.ultimo_aggiornamento = adesso

    async def _andamento(self, rif: RiferimentoTreno) -> Treno | None:
        async with self._limite:
            try:
                return await self.fonte.andamento(rif)
            except ErroreFonte as e:
                log.debug("Andamento di %s non disponibile: %s", rif.numero, e)
                return self.registro.treni.get(rif.chiave)  # tiene il dato precedente

    @staticmethod
    def _concluso(treno: Treno, adesso: datetime) -> bool:
        orario = stima_orario(treno, adesso)
        return bool(orario) and orario[-1].arrivo + MARGINE_DOPO_ARRIVO < adesso
