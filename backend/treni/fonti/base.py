"""Contratto comune a tutte le fonti di dati sui treni."""

from typing import Protocol

from treni.dominio.linea import Linea
from treni.dominio.treno import RiferimentoTreno, Treno, VoceTabellone


class ErroreFonte(Exception):
    """La fonte non ha risposto o ha risposto in modo inatteso."""


class FonteDati(Protocol):
    nome: str  # mostrato sullo schermo, es. "ViaggiaTreno" o "Demo"
    in_tempo_reale: bool

    async def prepara(self, linea: Linea) -> Linea:
        """Operazioni iniziali; può restituire la linea arricchita (es. codici stazione)."""
        ...

    async def scopri_treni(self, linea: Linea) -> list[RiferimentoTreno]:
        """Treni che passano ora, o tra poco, dalle stazioni della linea."""
        ...

    async def andamento(self, riferimento: RiferimentoTreno) -> Treno | None:
        """Stato aggiornato del treno, o None se la fonte non lo conosce."""
        ...

    async def cerca_stazioni(self, testo: str) -> list[tuple[str, str]]:
        """Stazioni il cui nome inizia per `testo`: [(nome, codice)]."""
        ...

    async def tabellone(self, codice_stazione: str) -> list[VoceTabellone]:
        """Treni in partenza e in arrivo nella stazione, da adesso."""
        ...

    async def coordinate(self, codice_stazione: str) -> tuple[float, float] | None:
        """(latitudine, longitudine) della stazione, se note."""
        ...

    async def chiudi(self) -> None: ...
