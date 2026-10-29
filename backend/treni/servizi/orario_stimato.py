"""Orario stimato di un treno: orari reali dove noti, altrimenti previsti.

Per gli eventi non ancora avvenuti si usa l'orario programmato più il ritardo
attuale. Se una stima è già nel passato ma l'evento non è stato rilevato,
il treno è più in ritardo di quanto dichiarato: gli eventi futuri vengono
spostati in avanti così che il primo cada "adesso".
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from treni.dominio.treno import Treno

ANTICIPO_ORIGINE = timedelta(minutes=5)  # quanto prima della partenza il treno è in stazione
SOSTA_DESTINAZIONE = timedelta(minutes=3)  # quanto resta visibile dopo l'arrivo
# Oltre questo scarto si assume un rilevamento mancante, non un ritardo vero.
MASSIMO_SPOSTAMENTO = timedelta(minutes=45)


@dataclass(frozen=True)
class PassaggioStimato:
    arrivo: datetime
    partenza: datetime


def _evento(reale, programmato, ritardo) -> tuple[datetime | None, bool]:
    if reale is not None:
        return reale, True
    if programmato is not None:
        return programmato + ritardo, False
    return None, False


def stima_orario(treno: Treno, adesso: datetime) -> list[PassaggioStimato]:
    ritardo = timedelta(minutes=max(treno.ritardo_min, 0))
    eventi: list[list] = []  # [ora, certo] per arrivo e partenza di ogni fermata
    for f in treno.fermate:
        arrivo = _evento(f.arrivo_reale, f.arrivo_programmato, ritardo)
        partenza = _evento(f.partenza_reale, f.partenza_programmata, ritardo)
        eventi.append(list(arrivo))
        eventi.append(list(partenza))

    _completa_estremi(eventi)
    _sposta_eventi_scaduti(eventi, adesso)
    _rendi_crescente(eventi)

    return [
        PassaggioStimato(arrivo=eventi[i][0], partenza=eventi[i + 1][0])
        for i in range(0, len(eventi), 2)
    ]


def _completa_estremi(eventi: list[list]) -> None:
    """Origine senza arrivo e destinazione senza partenza; buchi dai vicini."""
    for i, ev in enumerate(eventi):
        if ev[0] is not None:
            continue
        if i == 0 and len(eventi) > 1 and eventi[1][0] is not None:
            ev[0] = eventi[1][0] - ANTICIPO_ORIGINE
        elif i == len(eventi) - 1 and eventi[i - 1][0] is not None:
            ev[0] = eventi[i - 1][0] + SOSTA_DESTINAZIONE
        elif i % 2 == 1 and eventi[i - 1][0] is not None:
            ev[0] = eventi[i - 1][0]  # partenza mancante: uguale all'arrivo
        elif i % 2 == 0 and i + 1 < len(eventi) and eventi[i + 1][0] is not None:
            ev[0] = eventi[i + 1][0]  # arrivo mancante: uguale alla partenza
    for i, ev in enumerate(eventi):
        if ev[0] is None:  # ultima risorsa: copia il precedente noto
            ev[0] = eventi[i - 1][0] if i > 0 else None
    if eventi and eventi[0][0] is None:
        primo = next((e[0] for e in eventi if e[0] is not None), datetime.min)
        for ev in eventi:
            ev[0] = ev[0] or primo


def _sposta_eventi_scaduti(eventi: list[list], adesso: datetime) -> None:
    # L'arrivo all'origine e la partenza dalla destinazione sono convenzionali.
    ultimo_certo = max((i for i, ev in enumerate(eventi) if ev[1]), default=0)
    primo_incerto = next(
        (i for i, ev in enumerate(eventi) if i > max(ultimo_certo, 0) and not ev[1]), None
    )
    if primo_incerto is None or primo_incerto == len(eventi) - 1:
        return
    scarto = adesso - eventi[primo_incerto][0]
    if timedelta(0) < scarto <= MASSIMO_SPOSTAMENTO:
        for ev in eventi[primo_incerto:]:
            ev[0] = ev[0] + scarto


def _rendi_crescente(eventi: list[list]) -> None:
    for i in range(1, len(eventi)):
        if eventi[i][0] < eventi[i - 1][0]:
            eventi[i][0] = eventi[i - 1][0]
