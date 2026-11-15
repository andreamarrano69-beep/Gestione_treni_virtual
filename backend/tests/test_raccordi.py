from datetime import timedelta

import pytest

from tests.aiuti import linea_prova, minuti, treno_prova
from treni.dominio.circolazione import StatoTreno, TipoIncrocio
from treni.servizi.conflitti_bivio import prevedi_conflitti_bivio
from treni.servizi.incroci import campiona_traiettoria
from treni.servizi.orario_stimato import stima_orario
from treni.servizi.posizione import CalcolatorePosizione
from treni.servizi.raccordi import passaggi_raccordo, posizione_su_raccordo

LINEA = linea_prova()  # Alfa km 0, Beta 10, Gamma 30, Delta 40
CALCOLATORE = CalcolatorePosizione(LINEA)


def km_bivio(id_stazione):
    return LINEA.stazione(id_stazione).km


def sul_raccordo(treno, minuto):
    orario = stima_orario(treno, minuti(0))
    passaggi = passaggi_raccordo(CALCOLATORE, treno)
    return posizione_su_raccordo(passaggi, orario, km_bivio, minuti(minuto))


def test_treno_che_entra_da_fuori_linea():
    # Da Torino entra a Beta e prosegue verso Gamma (km crescenti): entra dal lato sinistro.
    treno = treno_prova("1", [("Torino", None, 0), ("Beta", 20, 21), ("Gamma", 41, None)])
    (passaggio,) = passaggi_raccordo(CALCOLATORE, treno)
    assert passaggio.entrata
    assert (passaggio.raccordo.stazione_id, passaggio.raccordo.lato, passaggio.raccordo.nome) == ("beta", "sinistra", "TORINO")

    p = sul_raccordo(treno, 15)
    assert p.stato == StatoTreno.SUL_RACCORDO
    assert p.avanzamento == pytest.approx(0.25)
    assert p.minuti_al_bivio == 5
    assert sul_raccordo(treno, -20) is None  # troppo lontano per mostrarlo


def test_treno_che_esce_dalla_linea():
    # Da Gamma verso Beta (km decrescenti), poi esce verso Roma: esce dal lato sinistro di Beta.
    treno = treno_prova("2", [("Gamma", None, 0), ("Beta", 20, 21), ("Roma", 41, None)])
    (passaggio,) = passaggi_raccordo(CALCOLATORE, treno)
    assert not passaggio.entrata
    assert passaggio.raccordo.lato == "sinistra"
    assert sul_raccordo(treno, 31).avanzamento == pytest.approx(0.5)


def test_treno_internazionale_che_parte_dal_capolinea():
    # Tocca solo Alfa (primo capolinea) e va all'estero: esce dal lato esterno.
    treno = treno_prova("3", [("Alfa", None, 0), ("Chiasso", 30, 31), ("Zurich HB", 120, None)])
    (passaggio,) = passaggi_raccordo(CALCOLATORE, treno)
    assert (passaggio.raccordo.lato, passaggio.direzione) == ("sinistra", -1)
    assert CALCOLATORE.tocca_la_linea(treno)


def test_conflitto_al_bivio():
    entra = treno_prova("1", [("Torino", None, 0), ("Beta", 20, 21), ("Gamma", 41, None)])
    passa = treno_prova("2", [("Alfa", None, 9), ("Beta", 19, 19), ("Gamma", 39, None)])
    adesso, orizzonte = minuti(0), timedelta(minutes=60)
    orari = {t.chiave: stima_orario(t, adesso) for t in (entra, passa)}
    traiettorie = {
        t.chiave: campiona_traiettoria(
            lambda istante, t=t: CALCOLATORE.posizione(t, orari[t.chiave], istante), adesso, orizzonte
        )
        for t in (entra, passa)
    }
    passaggi = {entra.chiave: (passaggi_raccordo(CALCOLATORE, entra), orari[entra.chiave])}
    conflitti = prevedi_conflitti_bivio(LINEA, passaggi, traiettorie, adesso, orizzonte)
    assert [(c.tipo, c.stazione_vicina_id) for c in conflitti] == [(TipoIncrocio.BIVIO, "beta")]
