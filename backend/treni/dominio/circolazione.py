"""Risultati dei calcoli: dove sta un treno e dove incrocerà gli altri."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class StatoTreno(str, Enum):
    IN_LINEA = "in_linea"  # in corsa tra due stazioni
    IN_STAZIONE = "in_stazione"  # fermo in una stazione
    SUL_RACCORDO = "sul_raccordo"  # su un'altra linea, in arrivo al bivio o appena uscito


@dataclass(frozen=True)
class PosizioneTreno:
    stato: StatoTreno
    km: float
    direzione: int  # +1 verso km crescenti, -1 verso km decrescenti
    stazione_id: str | None = None  # valorizzata se IN_STAZIONE
    binario: str | None = None
    da_stazione_id: str | None = None  # valorizzate se IN_LINEA
    a_stazione_id: str | None = None
    # Valorizzati se SUL_RACCORDO (stazione_id è la stazione del bivio):
    raccordo_id: str | None = None
    avanzamento: float | None = None  # 0 = al bivio, 1 = in fondo al raccordo
    entrata: bool | None = None  # True se sta entrando sulla linea, False se ne è uscito
    minuti_al_bivio: int | None = None  # solo in entrata


class TipoIncrocio(str, Enum):
    INCROCIO = "incrocio"  # treni in direzioni opposte
    PRECEDENZA = "precedenza"  # un treno ne supera un altro nella stessa direzione
    BIVIO = "bivio"  # due treni impegnano lo stesso bivio a pochi minuti di distanza


@dataclass(frozen=True)
class Incrocio:
    tipo: TipoIncrocio
    treno_a: str  # chiavi dei treni
    treno_b: str
    km: float
    ora: datetime
    stazione_vicina_id: str
