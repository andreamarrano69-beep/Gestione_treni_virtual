"""Orario inventato ma verosimile per provare il quadro senza internet."""

import random
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from treni.dominio.linea import Linea, Stazione
from treni.fonti.demo.tipi_demo import TIPI, TipoServizio

ROMA = ZoneInfo("Europe/Rome")


@dataclass(frozen=True)
class ServizioDemo:
    numero: str
    categoria: str
    stazioni: tuple[Stazione, ...]  # nell'ordine di marcia, comprese quelle fuori linea
    orari: tuple[tuple[datetime, datetime], ...]  # (arrivo, partenza) programmati
    ritardo_finale_min: int


def _fuori_linea(nome: str) -> Stazione:
    identificativo = re.sub(r"[^a-z0-9]+", "_", nome.lower()).strip("_")
    return Stazione(id=identificativo, nome=nome.title(), nome_vt=nome, km=0, binari=("1", "2"))


def _percorso(linea: Linea, tipo: TipoServizio) -> tuple[list[Stazione], list[float]]:
    """Fermate nel verso dei km crescenti e minuti di viaggio dalla precedente."""
    km_da, km_a = linea.stazione(tipo.da).km, linea.stazione(tipo.a).km
    sulla_linea = [
        s for s in linea.stazioni
        if km_da <= s.km <= km_a and (tipo.fermate is None or s.id in tipo.fermate)
    ]
    stazioni = [_fuori_linea(n) for n, _ in tipo.prima] + sulla_linea + [_fuori_linea(n) for n, _ in tipo.dopo]
    tempi = [0.0] + [float(m) for _, m in tipo.prima]
    for a, b in zip(sulla_linea, sulla_linea[1:]):
        tempi.append(round(abs(b.km - a.km) / tipo.velocita_kmh * 60 + 1.5))
    tempi += [float(m) for _, m in tipo.dopo]
    return stazioni, tempi


def _orari(tempi: list[float], partenza: datetime, sosta_min: float):
    orari, ora = [], partenza
    for i, minuti in enumerate(tempi):
        arrivo = ora + timedelta(minutes=minuti)
        sosta = 0 if i in (0, len(tempi) - 1) else sosta_min
        ora = arrivo + timedelta(minutes=sosta)
        orari.append((arrivo, ora))
    return tuple(orari)


def _ritardo(numero: int, giorno: date) -> int:
    rnd = random.Random(numero * 10000 + giorno.toordinal())
    fascia = rnd.random()
    if fascia < 0.6:
        return rnd.randint(0, 3)
    if fascia < 0.9:
        return rnd.randint(4, 12)
    return rnd.randint(13, 30)


def servizi_del_giorno(linea: Linea, giorno: date) -> list[ServizioDemo]:
    servizi = []
    for tipo in TIPI:
        stazioni, tempi = _percorso(linea, tipo)
        # Nel verso opposto le fermate si invertono e ogni tempo resta legato al suo tratto.
        versi = ((stazioni, tempi), (stazioni[::-1], [0.0] + tempi[:0:-1]))
        for crescente, (fermate, minuti) in zip((True, False), versi):
            inizio = datetime.combine(giorno, time(0, tipo.scostamento_min), ROMA)
            for k in range(24 * 60 // tipo.cadenza_min):
                numero = tipo.base_numero + 2 * k + (1 if crescente else 0)
                servizi.append(ServizioDemo(
                    numero=str(numero),
                    categoria=tipo.categoria,
                    stazioni=tuple(fermate),
                    orari=_orari(minuti, inizio + timedelta(minutes=k * tipo.cadenza_min), tipo.sosta_min),
                    ritardo_finale_min=_ritardo(numero, giorno),
                ))
    return servizi
