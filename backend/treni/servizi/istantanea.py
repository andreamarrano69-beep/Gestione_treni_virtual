"""Fotografia della circolazione in un istante: posizioni e incroci previsti."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from treni.dominio.circolazione import Incrocio, PosizioneTreno
from treni.dominio.linea import Linea
from treni.dominio.treno import Treno
from treni.servizi.incroci import campiona_traiettoria, prevedi_incroci
from treni.servizi.orario_stimato import PassaggioStimato, stima_orario
from treni.servizi.posizione import CalcolatorePosizione

VALIDITA_INCROCI = timedelta(seconds=10)  # gli incroci si ricalcolano al massimo ogni 10 s


@dataclass
class TrenoInCircolazione:
    treno: Treno
    orario: list[PassaggioStimato]
    posizione: PosizioneTreno | None  # None se non è (ancora) sulla linea


@dataclass
class Istantanea:
    adesso: datetime
    treni: list[TrenoInCircolazione]
    incroci: list[Incrocio]


class Fotografo:
    def __init__(self, orizzonte_incroci: timedelta):
        self._orizzonte = orizzonte_incroci
        self._incroci: list[Incrocio] = []
        self._incroci_calcolati: datetime | None = None

    def scatta(
        self, linea: Linea, calcolatore: CalcolatorePosizione, treni: list[Treno], adesso: datetime
    ) -> Istantanea:
        in_circolazione = []
        for treno in treni:
            orario = stima_orario(treno, adesso)
            posizione = calcolatore.posizione(treno, orario, adesso)
            in_circolazione.append(TrenoInCircolazione(treno, orario, posizione))

        if self._incroci_calcolati is None or adesso - self._incroci_calcolati > VALIDITA_INCROCI:
            self._incroci = self._calcola_incroci(linea, calcolatore, in_circolazione, adesso)
            self._incroci_calcolati = adesso
        incroci = [i for i in self._incroci if i.ora >= adesso]
        return Istantanea(adesso=adesso, treni=in_circolazione, incroci=incroci)

    def _calcola_incroci(self, linea, calcolatore, treni, adesso) -> list[Incrocio]:
        traiettorie = {
            t.treno.chiave: campiona_traiettoria(
                lambda istante, t=t: calcolatore.posizione(t.treno, t.orario, istante),
                adesso,
                self._orizzonte,
            )
            for t in treni
        }
        return prevedi_incroci(linea, traiettorie)
