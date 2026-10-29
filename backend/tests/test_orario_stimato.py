from tests.aiuti import minuti, treno_prova
from treni.servizi.orario_stimato import ANTICIPO_ORIGINE, SOSTA_DESTINAZIONE, stima_orario


def test_orario_in_orario_usa_il_programmato():
    treno = treno_prova("1", [("Alfa", None, 0), ("Beta", 10, 11), ("Gamma", 30, None)])
    orario = stima_orario(treno, minuti(0))
    assert orario[0].arrivo == minuti(0) - ANTICIPO_ORIGINE
    assert orario[1].arrivo == minuti(10)
    assert orario[1].partenza == minuti(11)
    assert orario[2].partenza == minuti(30) + SOSTA_DESTINAZIONE


def test_il_ritardo_sposta_gli_eventi_futuri():
    treno = treno_prova("1", [("Alfa", None, 0), ("Beta", 10, 11)], ritardo=5)
    treno.fermate[0].partenza_reale = minuti(5)
    orario = stima_orario(treno, minuti(6))
    assert orario[0].partenza == minuti(5)
    assert orario[1].arrivo == minuti(15)


def test_evento_scaduto_ma_non_rilevato_viene_spostato_ad_adesso():
    treno = treno_prova("1", [("Alfa", None, 0), ("Beta", 10, 11), ("Gamma", 30, None)])
    treno.fermate[0].partenza_reale = minuti(0)
    orario = stima_orario(treno, minuti(14))  # doveva arrivare a Beta alle 10
    assert orario[1].arrivo == minuti(14)
    assert orario[2].arrivo == minuti(34)


def test_scarto_enorme_non_viene_spostato():
    treno = treno_prova("1", [("Alfa", None, 0), ("Beta", 10, None)])
    treno.fermate[0].partenza_reale = minuti(0)
    orario = stima_orario(treno, minuti(200))
    assert orario[1].arrivo == minuti(10)
