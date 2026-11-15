"""Raccordi: i punti in cui i treni entrano sulla linea da un'altra o ne escono.

Un raccordo è identificato dalla stazione del bivio, dal lato della stazione e
dalla fermata fuori linea più vicina (es. Aversa, lato destro, Villa Literno).
Il bivio vero può stare tra due stazioni: qui si usa la prima (o l'ultima)
stazione della linea in cui il treno ferma.
"""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta

from treni.dominio.circolazione import PosizioneTreno, StatoTreno
from treni.dominio.treno import Treno
from treni.linee.abbinamento import normalizza_nome
from treni.servizi.lati import lato_e_direzione
from treni.servizi.orario_stimato import PassaggioStimato

ANTICIPO_AVVICINAMENTO = timedelta(minutes=10)  # da quando mostrare un treno in arrivo al bivio
PERMANENZA_USCITA = timedelta(minutes=2)  # quanto resta visibile dopo la fermata fuori linea


@dataclass(frozen=True)
class Raccordo:
    stazione_id: str
    lato: str  # "sinistra" (km minori) o "destra" (km maggiori)
    nome: str  # fermata fuori linea più vicina al bivio

    @property
    def id(self) -> str:
        return f"{self.stazione_id}|{self.lato}|{normalizza_nome(self.nome)}"


@dataclass(frozen=True)
class PassaggioRaccordo:
    raccordo: Raccordo
    entrata: bool
    direzione: int  # verso di marcia sulla linea
    indice_fuori: int  # indice della fermata fuori linea
    indice_linea: int  # indice della fermata del bivio


def passaggi_raccordo(calcolatore, treno: Treno) -> list[PassaggioRaccordo]:
    """Entrata e uscita del treno dalla linea, se arriva da fuori o prosegue fuori."""
    stazioni = calcolatore.stazioni_di(treno)
    sulla_linea = [i for i, s in enumerate(stazioni) if s]
    if not sulla_linea:
        return []
    passaggi = []
    primo, ultimo = sulla_linea[0], sulla_linea[-1]
    if primo > 0:
        passaggi.append(_passaggio(calcolatore, treno, stazioni, primo, primo - 1, entrata=True))
    if ultimo < len(stazioni) - 1:
        passaggi.append(_passaggio(calcolatore, treno, stazioni, ultimo, ultimo + 1, entrata=False))
    return passaggi


def _passaggio(calcolatore, treno, stazioni, i_linea, i_fuori, entrata) -> PassaggioRaccordo:
    stazione = stazioni[i_linea]
    verso = calcolatore.direzione_vicino(stazioni, i_linea)
    lato, direzione = lato_e_direzione(calcolatore.linea, stazione, entrata, verso)
    raccordo = Raccordo(stazione.id, lato, treno.fermate[i_fuori].nome)
    return PassaggioRaccordo(raccordo, entrata, direzione, i_fuori, i_linea)


def ora_al_bivio(p: PassaggioRaccordo, orario: list[PassaggioStimato]) -> datetime:
    return orario[p.indice_linea].arrivo if p.entrata else orario[p.indice_linea].partenza


def posizione_su_raccordo(
    passaggi: list[PassaggioRaccordo], orario: list[PassaggioStimato], km_bivio, istante: datetime
) -> PosizioneTreno | None:
    """km_bivio(stazione_id) -> km della stazione del bivio."""
    for p in passaggi:
        if p.entrata:
            inizio, fine = orario[p.indice_fuori].partenza, orario[p.indice_linea].arrivo
            if not (inizio - ANTICIPO_AVVICINAMENTO <= istante < fine):
                continue
            avanzamento = 1 - _frazione(inizio, fine, istante)
            minuti = math.ceil((fine - istante).total_seconds() / 60)
        else:
            inizio, fine = orario[p.indice_linea].partenza, orario[p.indice_fuori].arrivo
            if not (inizio < istante <= fine + PERMANENZA_USCITA):
                continue
            avanzamento, minuti = _frazione(inizio, fine, istante), None
        return PosizioneTreno(
            stato=StatoTreno.SUL_RACCORDO,
            km=km_bivio(p.raccordo.stazione_id),
            direzione=p.direzione,
            stazione_id=p.raccordo.stazione_id,
            raccordo_id=p.raccordo.id,
            avanzamento=round(avanzamento, 3),
            entrata=p.entrata,
            minuti_al_bivio=minuti,
        )
    return None


def _frazione(inizio: datetime, fine: datetime, istante: datetime) -> float:
    durata = (fine - inizio).total_seconds()
    if durata <= 0:
        return 1.0
    return min(max((istante - inizio).total_seconds() / durata, 0.0), 1.0)
