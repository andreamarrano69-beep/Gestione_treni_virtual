"""Conflitti al bivio: un treno entra o esce dalla linea mentre un altro
passa (o parte) dalla stessa stazione a pochi minuti di distanza.

Nella realtà uno dei due deve aspettare: è il caso che il regolatore della
circolazione deve risolvere dando la precedenza.
"""

from datetime import datetime, timedelta

from treni.dominio.circolazione import Incrocio, TipoIncrocio
from treni.dominio.linea import Linea
from treni.servizi.incroci import Traiettoria
from treni.servizi.orario_stimato import PassaggioStimato
from treni.servizi.raccordi import PassaggioRaccordo, ora_al_bivio

FINESTRA = timedelta(minutes=3)


def passaggio_dal_km(traiettoria: Traiettoria, km: float) -> datetime | None:
    """Quando la traiettoria passa dal km. Se è già ferma lì, quando riparte."""
    if traiettoria and traiettoria[0] and traiettoria[0][1] == km:
        return next((c[0] for c in traiettoria if c and c[1] != km), None)
    for a, b in zip(traiettoria, traiettoria[1:]):
        if not (a and b):
            continue
        if b[1] == km:
            return b[0]
        if (a[1] - km) * (b[1] - km) < 0:
            frazione = (km - a[1]) / (b[1] - a[1])
            return a[0] + (b[0] - a[0]) * frazione
    return None


def prevedi_conflitti_bivio(
    linea: Linea,
    passaggi: dict[str, tuple[list[PassaggioRaccordo], list[PassaggioStimato]]],
    traiettorie: dict[str, Traiettoria],
    adesso: datetime,
    orizzonte: timedelta,
) -> list[Incrocio]:
    """passaggi: chiave treno -> (passaggi di raccordo, orario stimato)."""
    conflitti, visti = [], set()
    for chiave, (suoi_passaggi, orario) in passaggi.items():
        for p in suoi_passaggi:
            ora = ora_al_bivio(p, orario)
            if not (adesso <= ora <= adesso + orizzonte):
                continue
            stazione = linea.stazione(p.raccordo.stazione_id)
            for altra, traiettoria in traiettorie.items():
                coppia = (frozenset((chiave, altra)), stazione.id)
                if altra == chiave or coppia in visti:
                    continue
                ora_altra = passaggio_dal_km(traiettoria, stazione.km)
                if ora_altra is None or abs(ora_altra - ora) > FINESTRA:
                    continue
                visti.add(coppia)
                conflitti.append(Incrocio(
                    tipo=TipoIncrocio.BIVIO,
                    treno_a=chiave,
                    treno_b=altra,
                    km=stazione.km,
                    ora=min(ora, ora_altra),
                    stazione_vicina_id=stazione.id,
                ))
    return conflitti
