"""Chilometriche approssimate delle fermate di una linea ricavata dai treni.

Se la fonte conosce le coordinate delle stazioni si usa la distanza in linea
d'aria (un po' meno di quella sui binari); altrimenti si stima dai tempi di
percorrenza del treno.
"""

from math import asin, cos, radians, sin, sqrt

from treni.dominio.treno import Fermata
from treni.fonti.base import FonteDati

RAGGIO_TERRA_KM = 6371
KM_AL_MINUTO = 1.2  # velocità media di un regionale, circa 72 km/h
KM_SENZA_DATI = 5


def distanza_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(radians, (*a, *b))
    h = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * RAGGIO_TERRA_KM * asin(sqrt(h))


def _km_da_tempi(a: Fermata, b: Fermata) -> float:
    partenza = a.partenza_programmata or a.arrivo_programmato
    arrivo = b.arrivo_programmato or b.partenza_programmata
    if not (partenza and arrivo):
        return KM_SENZA_DATI
    minuti = abs((arrivo - partenza).total_seconds()) / 60
    return max(minuti * KM_AL_MINUTO, 1)


async def progressive_km(fonte: FonteDati, fermate: list[Fermata]) -> list[float]:
    coordinate = [await fonte.coordinate(f.codice) if f.codice else None for f in fermate]
    usa_coordinate = all(coordinate)
    progressive = [0.0]
    for i in range(1, len(fermate)):
        if usa_coordinate:
            passo = max(distanza_km(coordinate[i - 1], coordinate[i]), 0.5)
        else:
            passo = _km_da_tempi(fermate[i - 1], fermate[i])
        progressive.append(round(progressive[-1] + passo, 1))
    return progressive
