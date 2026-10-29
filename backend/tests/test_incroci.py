from datetime import timedelta

import pytest

from tests.aiuti import linea_prova, minuti, treno_prova
from treni.dominio.circolazione import TipoIncrocio
from treni.servizi.incroci import campiona_traiettoria, prevedi_incroci
from treni.servizi.orario_stimato import stima_orario
from treni.servizi.posizione import CalcolatorePosizione


def traiettorie(treni):
    linea = linea_prova()
    calcolatore = CalcolatorePosizione(linea)
    adesso = minuti(0)
    risultato = {}
    for treno in treni:
        orario = stima_orario(treno, adesso)
        risultato[treno.chiave] = campiona_traiettoria(
            lambda istante, t=treno, o=orario: calcolatore.posizione(t, o, istante),
            adesso,
            timedelta(minutes=30),
        )
    return linea, risultato


def test_incrocio_tra_treni_opposti():
    andata = treno_prova("1", [("Beta", None, 0), ("Gamma", 20, None)])
    ritorno = treno_prova("2", [("Gamma", None, 0), ("Beta", 20, None)])
    linea, tr = traiettorie([andata, ritorno])
    incroci = prevedi_incroci(linea, tr)
    assert len(incroci) == 1
    assert incroci[0].tipo == TipoIncrocio.INCROCIO
    assert incroci[0].km == pytest.approx(20, abs=0.5)
    assert incroci[0].ora == pytest.approx(minuti(10), abs=timedelta(seconds=30))


def test_precedenza_quando_un_treno_veloce_supera():
    lento = treno_prova("1", [("Alfa", None, 0), ("Beta", 30, None)])
    veloce = treno_prova("2", [("Alfa", None, 5), ("Beta", 15, None)])
    linea, tr = traiettorie([lento, veloce])
    incroci = prevedi_incroci(linea, tr)
    assert [i.tipo for i in incroci] == [TipoIncrocio.PRECEDENZA]
