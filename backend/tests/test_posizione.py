import pytest

from tests.aiuti import linea_prova, minuti, treno_prova
from treni.dominio.circolazione import StatoTreno
from treni.servizi.orario_stimato import stima_orario
from treni.servizi.posizione import CalcolatorePosizione


@pytest.fixture
def calcolatore():
    return CalcolatorePosizione(linea_prova())


def posizione(calcolatore, treno, minuto):
    istante = minuti(minuto)
    return calcolatore.posizione(treno, stima_orario(treno, minuti(0)), istante)


def test_treno_a_meta_tratta(calcolatore):
    treno = treno_prova("1", [("Alfa", None, 0), ("Beta", 10, 12), ("Gamma", 32, None)])
    p = posizione(calcolatore, treno, 22)
    assert p.stato == StatoTreno.IN_LINEA
    assert p.km == pytest.approx(20)
    assert p.direzione == 1
    assert (p.da_stazione_id, p.a_stazione_id) == ("beta", "gamma")


def test_treno_fermo_in_stazione_col_binario(calcolatore):
    treno = treno_prova("1", [("Alfa", None, 0), ("Beta", 10, 12), ("Gamma", 32, None)])
    p = posizione(calcolatore, treno, 11)
    assert p.stato == StatoTreno.IN_STAZIONE
    assert p.stazione_id == "beta"
    assert p.binario == "2"


def test_direzione_decrescente(calcolatore):
    treno = treno_prova("2", [("Gamma", None, 0), ("Beta", 20, None)])
    p = posizione(calcolatore, treno, 5)
    assert p.direzione == -1
    assert p.km == pytest.approx(25)


def test_treno_che_arriva_da_fuori_linea_compare_solo_sulla_linea(calcolatore):
    treno = treno_prova("3", [("Torino", None, 0), ("Alfa", 60, 61), ("Beta", 71, None)])
    assert posizione(calcolatore, treno, 30) is None
    assert posizione(calcolatore, treno, 60).stazione_id == "alfa"
    assert posizione(calcolatore, treno, 66).stato == StatoTreno.IN_LINEA


def test_salto_troppo_lungo_non_e_sulla_linea(calcolatore):
    # Alfa-Delta è 40 km, oltre il massimo di 25: il treno corre su un'altra linea.
    treno = treno_prova("4", [("Alfa", None, 0), ("Delta", 20, None)])
    assert not calcolatore.percorre_la_linea(treno)
    assert posizione(calcolatore, treno, 10) is None
