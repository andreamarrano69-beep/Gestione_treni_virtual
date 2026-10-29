"""Risultati dei calcoli: dove sta un treno e dove incrocerà gli altri."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class StatoTreno(str, Enum):
    IN_LINEA = "in_linea"  # in corsa tra due stazioni
    IN_STAZIONE = "in_stazione"  # fermo in una stazione


@dataclass(frozen=True)
class PosizioneTreno:
    stato: StatoTreno
    km: float
    direzione: int  # +1 verso km crescenti, -1 verso km decrescenti
    stazione_id: str | None = None  # valorizzata se IN_STAZIONE
    binario: str | None = None
    da_stazione_id: str | None = None  # valorizzate se IN_LINEA
    a_stazione_id: str | None = None


class TipoIncrocio(str, Enum):
    INCROCIO = "incrocio"  # treni in direzioni opposte
    PRECEDENZA = "precedenza"  # un treno ne supera un altro nella stessa direzione


@dataclass(frozen=True)
class Incrocio:
    tipo: TipoIncrocio
    treno_a: str  # chiavi dei treni
    treno_b: str
    km: float
    ora: datetime
    stazione_vicina_id: str
