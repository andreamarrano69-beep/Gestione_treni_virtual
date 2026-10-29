"""Calcola dove si trova un treno sulla linea in un certo istante.

La posizione tra due stazioni è interpolata in proporzione al tempo trascorso
tra la partenza dalla prima e l'arrivo alla seconda: ViaggiaTreno non fornisce
il GPS, solo i passaggi nelle località di servizio.
"""

from datetime import datetime

from treni.dominio.circolazione import PosizioneTreno, StatoTreno
from treni.dominio.linea import Linea, Stazione
from treni.dominio.treno import Treno
from treni.linee.abbinamento import Abbinatore
from treni.servizi.orario_stimato import PassaggioStimato


class CalcolatorePosizione:
    def __init__(self, linea: Linea):
        self._linea = linea
        self._abbinatore = Abbinatore(linea)

    def stazioni_di(self, treno: Treno) -> list[Stazione | None]:
        """Per ogni fermata del treno, la stazione della linea (o None)."""
        return [self._abbinatore.stazione_di(f) for f in treno.fermate]

    def tratto_valido(self, a: Stazione | None, b: Stazione | None) -> bool:
        return (
            a is not None
            and b is not None
            and a.id != b.id
            and abs(a.km - b.km) <= self._linea.max_salto_km
        )

    def percorre_la_linea(self, treno: Treno) -> bool:
        stazioni = self.stazioni_di(treno)
        return any(self.tratto_valido(a, b) for a, b in zip(stazioni, stazioni[1:]))

    def posizione(
        self, treno: Treno, orario: list[PassaggioStimato], istante: datetime
    ) -> PosizioneTreno | None:
        stazioni = self.stazioni_di(treno)
        for i, (passaggio, stazione) in enumerate(zip(orario, stazioni)):
            if istante < passaggio.arrivo:
                return None  # non è ancora arrivato su questo punto
            if istante <= passaggio.partenza:
                return self._in_stazione(treno, stazioni, i) if stazione else None
            if i + 1 < len(orario) and istante < orario[i + 1].arrivo:
                return self._in_linea(stazioni, orario, i, istante)
        return None

    def _in_stazione(self, treno: Treno, stazioni, i: int) -> PosizioneTreno | None:
        fermata = treno.fermate[i]
        stazione = stazioni[i]
        if fermata.soppressa:
            return None
        direzione = self._direzione_vicino(stazioni, i)
        if direzione is None:
            return None  # unica fermata sulla linea: non la percorre
        return PosizioneTreno(
            stato=StatoTreno.IN_STAZIONE,
            km=stazione.km,
            direzione=direzione,
            stazione_id=stazione.id,
            binario=fermata.binario,
        )

    def _in_linea(self, stazioni, orario, i: int, istante: datetime) -> PosizioneTreno | None:
        a, b = stazioni[i], stazioni[i + 1]
        if not self.tratto_valido(a, b):
            return None
        inizio, fine = orario[i].partenza, orario[i + 1].arrivo
        durata = (fine - inizio).total_seconds()
        frazione = (istante - inizio).total_seconds() / durata if durata > 0 else 1.0
        return PosizioneTreno(
            stato=StatoTreno.IN_LINEA,
            km=a.km + (b.km - a.km) * min(max(frazione, 0.0), 1.0),
            direzione=1 if b.km > a.km else -1,
            da_stazione_id=a.id,
            a_stazione_id=b.id,
        )

    def _direzione_vicino(self, stazioni, i: int) -> int | None:
        """Direzione del tratto di linea successivo, o in mancanza del precedente."""
        if i + 1 < len(stazioni) and self.tratto_valido(stazioni[i], stazioni[i + 1]):
            return 1 if stazioni[i + 1].km > stazioni[i].km else -1
        if i > 0 and self.tratto_valido(stazioni[i - 1], stazioni[i]):
            return 1 if stazioni[i].km > stazioni[i - 1].km else -1
        return None
