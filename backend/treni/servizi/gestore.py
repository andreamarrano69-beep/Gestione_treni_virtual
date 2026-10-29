"""Tiene la linea attiva e permette di cambiarla mentre il programma gira."""

import asyncio
from datetime import timedelta

from treni.config import Impostazioni
from treni.dominio.linea import Linea
from treni.fonti.base import FonteDati
from treni.servizi.aggiornatore import Aggiornatore
from treni.servizi.istantanea import Fotografo


class GestoreLinea:
    def __init__(self, fonte: FonteDati, impostazioni: Impostazioni):
        self.fonte = fonte
        self._imp = impostazioni
        self.aggiornatore: Aggiornatore | None = None
        self.fotografo = self._nuovo_fotografo()
        self._cambio = asyncio.Lock()

    def _nuovo_fotografo(self) -> Fotografo:
        return Fotografo(timedelta(minutes=self._imp.orizzonte_incroci_min))

    async def attiva(self, linea: Linea) -> None:
        async with self._cambio:
            if self.aggiornatore:
                await self.aggiornatore.ferma()
            self.aggiornatore = Aggiornatore(self.fonte, linea, self._imp)
            self.fotografo = self._nuovo_fotografo()
            self.aggiornatore.avvia()

    async def chiudi(self) -> None:
        if self.aggiornatore:
            await self.aggiornatore.ferma()
        await self.fonte.chiudi()
