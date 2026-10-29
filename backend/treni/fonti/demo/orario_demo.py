"""Orario inventato ma verosimile per provare il quadro senza internet."""

import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from treni.dominio.linea import Linea, Stazione

ROMA = ZoneInfo("Europe/Rome")


@dataclass(frozen=True)
class TipoServizio:
    categoria: str
    da: str  # id stazione di partenza (nel verso crescente)
    a: str
    fermate: tuple[str, ...] | None  # None = ferma ovunque tra da e a
    cadenza_min: int
    scostamento_min: int  # minuto della prima partenza
    velocita_kmh: float
    sosta_min: float
    base_numero: int


TIPI = (
    TipoServizio("REG", "milano_c", "piacenza", None, 30, 5, 70, 1, 2600),
    TipoServizio("REG", "piacenza", "bologna_c", None, 30, 20, 75, 1, 3900),
    TipoServizio("RV", "milano_c", "bologna_c",
                 ("milano_c", "rogoredo", "lodi", "codogno", "piacenza", "fidenza",
                  "parma", "reggio_e", "modena", "bologna_c"), 60, 25, 100, 2, 2100),
    TipoServizio("IC", "milano_c", "bologna_c",
                 ("milano_c", "rogoredo", "piacenza", "parma", "reggio_e", "modena",
                  "bologna_c"), 120, 50, 125, 2, 600),
)


@dataclass(frozen=True)
class ServizioDemo:
    numero: str
    categoria: str
    stazioni: tuple[Stazione, ...]  # nell'ordine di marcia
    orari: tuple[tuple[datetime, datetime], ...]  # (arrivo, partenza) programmati
    ritardo_finale_min: int


def _percorso(linea: Linea, tipo: TipoServizio, crescente: bool) -> tuple[Stazione, ...]:
    km_da, km_a = linea.stazione(tipo.da).km, linea.stazione(tipo.a).km
    stazioni = [
        s for s in linea.stazioni
        if km_da <= s.km <= km_a and (tipo.fermate is None or s.id in tipo.fermate)
    ]
    return tuple(stazioni if crescente else reversed(stazioni))


def _orari(stazioni, partenza: datetime, tipo: TipoServizio):
    orari, ora = [], partenza
    for i, s in enumerate(stazioni):
        arrivo = ora
        if i > 0:
            minuti = abs(s.km - stazioni[i - 1].km) / tipo.velocita_kmh * 60 + 1.5
            arrivo = ora + timedelta(minutes=round(minuti))
        sosta = 0 if i in (0, len(stazioni) - 1) else tipo.sosta_min
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
        for crescente in (True, False):
            stazioni = _percorso(linea, tipo, crescente)
            inizio = datetime.combine(giorno, time(0, tipo.scostamento_min), ROMA)
            for k in range(24 * 60 // tipo.cadenza_min):
                numero = tipo.base_numero + 2 * k + (1 if crescente else 0)
                partenza = inizio + timedelta(minutes=k * tipo.cadenza_min)
                servizi.append(ServizioDemo(
                    numero=str(numero),
                    categoria=tipo.categoria,
                    stazioni=stazioni,
                    orari=_orari(stazioni, partenza, tipo),
                    ritardo_finale_min=_ritardo(numero, giorno),
                ))
    return servizi
