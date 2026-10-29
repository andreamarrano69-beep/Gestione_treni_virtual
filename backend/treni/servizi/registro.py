"""Memoria dei treni seguiti e dello stato della fonte dati."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from treni.dominio.treno import Treno

DURATA_IGNORATO = timedelta(hours=6)


@dataclass
class StatoFonte:
    nome: str
    in_tempo_reale: bool
    ok: bool = True
    messaggio: str = "In avvio…"
    ultimo_aggiornamento: datetime | None = None


@dataclass
class RegistroTreni:
    treni: dict[str, Treno] = field(default_factory=dict)
    # Treni che non percorrono la linea: non vanno richiesti di nuovo per un po'.
    _ignorati: dict[str, datetime] = field(default_factory=dict)

    def ignora(self, chiave: str, adesso: datetime) -> None:
        self.treni.pop(chiave, None)
        self._ignorati[chiave] = adesso + DURATA_IGNORATO

    def e_ignorato(self, chiave: str, adesso: datetime) -> bool:
        scadenza = self._ignorati.get(chiave)
        if scadenza is None:
            return False
        if scadenza < adesso:
            del self._ignorati[chiave]
            return False
        return True
