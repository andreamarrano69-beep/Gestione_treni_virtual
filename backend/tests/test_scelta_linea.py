"""Percorso completo della finestra "Scegli linea" con la fonte demo."""

import shutil
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from treni.app import crea_app
from treni.config import carica_impostazioni
from treni.servizi.distanze import distanza_km


@pytest.fixture
def client(tmp_path):
    imp = carica_impostazioni()
    cartella = tmp_path / "linee"
    shutil.copytree(imp.cartella_linee, cartella)
    imp = replace(imp, fonte="demo", cartella_linee=cartella, cartella_cache=tmp_path / "cache")
    with TestClient(crea_app(imp)) as c:
        c.get("/api/stato")  # lascia partire il primo ciclo della fonte
        yield c, cartella


def test_cerca_stazione_destinazioni_e_crea_linea(client):
    c, cartella = client
    stazioni = c.get("/api/stazioni", params={"testo": "lod"}).json()
    assert stazioni == [{"nome": "LODI", "codice": "DEMO-lodi"}]

    destinazioni = c.get("/api/stazioni/DEMO-lodi/destinazioni", params={"nome": "LODI"}).json()
    capolinea = [d["capolinea"] for d in destinazioni]
    assert "PIACENZA" in capolinea and "MILANO CENTRALE" in capolinea

    linea = c.post("/api/linee/crea", json={"codice": "DEMO-lodi", "nome": "LODI", "capolinea": "PIACENZA"}).json()
    nomi = [s["nome"] for s in linea["stazioni"]]
    assert nomi == ["Lodi", "Codogno", "Piacenza"]
    assert [s["km"] for s in linea["stazioni"]] == sorted(s["km"] for s in linea["stazioni"])
    assert (cartella / f"{linea['id']}.yaml").exists()

    assert c.get("/api/linea").json()["id"] == linea["id"]
    elenco = c.get("/api/linee").json()
    assert elenco["attiva"] == linea["id"]


def test_ritorno_a_una_linea_salvata(client):
    c, _ = client
    assert c.post("/api/linee/attiva", json={"id": "milano_bologna"}).json()["id"] == "milano_bologna"
    assert c.post("/api/linee/attiva", json={"id": "non_esiste"}).status_code == 404


def test_distanza_milano_bologna_in_linea_d_aria():
    assert distanza_km((45.486, 9.204), (44.506, 11.343)) == pytest.approx(200, abs=10)
