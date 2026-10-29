import json
from datetime import datetime, timezone
from pathlib import Path

from treni.dominio.treno import RiferimentoTreno
from treni.fonti.viaggiatreno.client import formato_data_vt
from treni.fonti.viaggiatreno.parser import riferimento_da_tabellone, treno_da_andamento, voce_tabellone

DATI = Path(__file__).parent / "dati"


def test_andamento_convertito_in_treno():
    dati = json.loads((DATI / "andamento_esempio.json").read_text(encoding="utf-8"))
    rif = RiferimentoTreno(numero="2645", cod_origine="S01700", data_partenza_ms=1793232000000)
    treno = treno_da_andamento(dati, rif)

    assert treno.sigla == "REG 2645"
    assert treno.categoria == "REG"
    assert treno.ritardo_min == 4
    assert [f.nome for f in treno.fermate] == ["MILANO CENTRALE", "LODI", "FIORENZUOLA", "PIACENZA"]
    assert treno.fermate[0].partenza_reale is not None
    assert treno.fermate[1].binario == "3"  # binario effettivo prevale sul programmato
    assert treno.fermate[2].soppressa
    assert treno.fermate[3].arrivo_reale is None
    assert treno.ultimo_rilevamento_luogo == "LODI"


def test_riga_tabellone():
    voce = {"numeroTreno": 2645, "codOrigine": "S01700", "dataPartenzaTreno": 1793232000000}
    rif = riferimento_da_tabellone(voce)
    assert rif.chiave == "S01700-2645-1793232000000"
    assert riferimento_da_tabellone({"numeroTreno": 1}) is None


def test_formato_data_come_javascript():
    istante = datetime(2026, 10, 29, 9, 5, tzinfo=timezone.utc)
    assert formato_data_vt(istante) == "Thu Oct 29 2026 10:05:00 GMT+0100"


def test_voci_del_tabellone_partenze_e_arrivi():
    voce = {
        "numeroTreno": 2645, "codOrigine": "S01700", "dataPartenzaTreno": 1793232000000,
        "compNumeroTreno": "REG 2645", "destinazione": "PIACENZA", "origine": "MILANO CENTRALE",
    }
    partenza = voce_tabellone(voce, "partenza")
    arrivo = voce_tabellone(voce, "arrivo")
    assert (partenza.categoria, partenza.capolinea) == ("REG", "PIACENZA")
    assert arrivo.capolinea == "MILANO CENTRALE"
