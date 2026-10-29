"""Prova completa: l'applicazione con la fonte demo risponde con treni e incroci."""

from dataclasses import replace

from fastapi.testclient import TestClient

from treni.app import crea_app
from treni.config import carica_impostazioni
from treni.linee.caricatore import carica_linea


def test_linea_milano_bologna_caricata():
    imp = carica_impostazioni()
    linea = carica_linea(imp.cartella_linee, "milano_bologna")
    assert linea.stazioni[0].id == "milano_c"
    assert linea.stazioni[-1].id == "bologna_c"
    assert all(a.km < b.km for a, b in zip(linea.stazioni, linea.stazioni[1:]))


def test_stato_con_fonte_demo():
    imp = replace(carica_impostazioni(), fonte="demo")
    with TestClient(crea_app(imp)) as client:
        linea = client.get("/api/linea").json()
        assert len(linea["stazioni"]) == 14

        stato = client.get("/api/stato").json()
        assert stato["fonte"]["nome"] == "Demo"
        sulla_linea = [t for t in stato["treni"] if t["posizione"]]
        assert sulla_linea, "la demo deve avere treni in circolazione a ogni ora"

        chiave = sulla_linea[0]["chiave"]
        dettaglio = client.get(f"/api/treni/{chiave}").json()
        assert dettaglio["fermate"]

        assert client.get("/").status_code == 200
