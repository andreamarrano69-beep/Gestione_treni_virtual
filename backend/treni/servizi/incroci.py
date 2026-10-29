"""Prevede dove e quando due treni si incroceranno sulla linea.

Per ogni treno si campiona la posizione futura a intervalli regolari; quando
la differenza di chilometrica tra due treni cambia segno, si sono incrociati
(direzioni opposte) o uno ha superato l'altro (stessa direzione).
"""

from datetime import datetime, timedelta
from itertools import combinations

from treni.dominio.circolazione import Incrocio, TipoIncrocio
from treni.dominio.linea import Linea

PASSO = timedelta(seconds=30)

# Per ogni treno: lista di (istante, km, direzione) oppure None se fuori linea.
Traiettoria = list[tuple[datetime, float, int] | None]


def campiona_traiettoria(posizione_a, adesso: datetime, orizzonte: timedelta) -> Traiettoria:
    """posizione_a(istante) -> PosizioneTreno | None"""
    campioni: Traiettoria = []
    istante = adesso
    while istante <= adesso + orizzonte:
        pos = posizione_a(istante)
        campioni.append((istante, pos.km, pos.direzione) if pos else None)
        istante += PASSO
    return campioni


def prevedi_incroci(linea: Linea, traiettorie: dict[str, Traiettoria]) -> list[Incrocio]:
    incroci = []
    for (chiave_a, ta), (chiave_b, tb) in combinations(traiettorie.items(), 2):
        incrocio = _primo_incrocio(linea, chiave_a, ta, chiave_b, tb)
        if incrocio:
            incroci.append(incrocio)
    return sorted(incroci, key=lambda x: x.ora)


def _primo_incrocio(linea, chiave_a, ta, chiave_b, tb) -> Incrocio | None:
    for k in range(min(len(ta), len(tb)) - 1):
        a0, a1, b0, b1 = ta[k], ta[k + 1], tb[k], tb[k + 1]
        if not (a0 and a1 and b0 and b1):
            continue
        d0, d1 = a0[1] - b0[1], a1[1] - b1[1]
        if d0 == 0 or d0 * d1 > 0:
            continue  # nessun cambio di segno in questo intervallo
        frazione = d0 / (d0 - d1)
        km = a0[1] + (a1[1] - a0[1]) * frazione
        ora = a0[0] + (a1[0] - a0[0]) * frazione
        tipo = TipoIncrocio.INCROCIO if a1[2] != b1[2] else TipoIncrocio.PRECEDENZA
        return Incrocio(
            tipo=tipo,
            treno_a=chiave_a,
            treno_b=chiave_b,
            km=round(km, 2),
            ora=ora,
            stazione_vicina_id=linea.stazione_piu_vicina(km).id,
        )
    return None
