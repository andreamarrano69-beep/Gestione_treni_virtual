"""Fotografia della circolazione in un istante: posizioni, raccordi e incroci previsti."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from treni.dominio.circolazione import Incrocio, PosizioneTreno
from treni.dominio.linea import Linea
from treni.dominio.treno import Treno
from treni.servizi.conflitti_bivio import prevedi_conflitti_bivio
from treni.servizi.incroci import campiona_traiettoria, prevedi_incroci
from treni.servizi.orario_stimato import PassaggioStimato, stima_orario
from treni.servizi.posizione import CalcolatorePosizione
from treni.servizi.raccordi import PassaggioRaccordo, Raccordo, passaggi_raccordo, posizione_su_raccordo

VALIDITA_INCROCI = timedelta(seconds=10)  # gli incroci si ricalcolano al massimo ogni 10 s


@dataclass
class TrenoInCircolazione:
    treno: Treno
    orario: list[PassaggioStimato]
    passaggi: list[PassaggioRaccordo]  # entrata e uscita dalla linea, se ci sono
    posizione: PosizioneTreno | None  # None se non è visibile né sulla linea né su un raccordo


@dataclass
class Istantanea:
    adesso: datetime
    treni: list[TrenoInCircolazione]
    incroci: list[Incrocio]
    raccordi: list[Raccordo]


class Fotografo:
    def __init__(self, orizzonte_incroci: timedelta):
        self._orizzonte = orizzonte_incroci
        self._incroci: list[Incrocio] = []
        self._incroci_calcolati: datetime | None = None

    def scatta(
        self, linea: Linea, calcolatore: CalcolatorePosizione, treni: list[Treno], adesso: datetime
    ) -> Istantanea:
        km_bivio = lambda id_stazione: linea.stazione(id_stazione).km  # noqa: E731
        in_circolazione, raccordi = [], {}
        for treno in treni:
            orario = stima_orario(treno, adesso)
            passaggi = passaggi_raccordo(calcolatore, treno)
            posizione = calcolatore.posizione(treno, orario, adesso) or posizione_su_raccordo(
                passaggi, orario, km_bivio, adesso
            )
            in_circolazione.append(TrenoInCircolazione(treno, orario, passaggi, posizione))
            raccordi.update((p.raccordo.id, p.raccordo) for p in passaggi)

        if self._incroci_calcolati is None or adesso - self._incroci_calcolati > VALIDITA_INCROCI:
            self._incroci = self._calcola_incroci(linea, calcolatore, in_circolazione, adesso)
            self._incroci_calcolati = adesso
        incroci = [i for i in self._incroci if i.ora >= adesso]
        ordinati = sorted(raccordi.values(), key=lambda r: r.id)
        return Istantanea(adesso=adesso, treni=in_circolazione, incroci=incroci, raccordi=ordinati)

    def _calcola_incroci(self, linea, calcolatore, treni, adesso) -> list[Incrocio]:
        traiettorie = {
            t.treno.chiave: campiona_traiettoria(
                lambda istante, t=t: calcolatore.posizione(t.treno, t.orario, istante),
                adesso,
                self._orizzonte,
            )
            for t in treni
        }
        passaggi = {t.treno.chiave: (t.passaggi, t.orario) for t in treni if t.passaggi}
        incroci = prevedi_incroci(linea, traiettorie)
        incroci += prevedi_conflitti_bivio(linea, passaggi, traiettorie, adesso, self._orizzonte)
        return sorted(incroci, key=lambda i: i.ora)
