"""Converte il JSON di ViaggiaTreno negli oggetti del dominio.

Il formato non è documentato: ogni campo viene letto con prudenza.
"""

from datetime import datetime, timezone

from treni.dominio.treno import Fermata, RiferimentoTreno, Treno

FERMATA_SOPPRESSA = 3  # valore di actualFermataType


def _ora(ms) -> datetime | None:
    if not ms:
        return None
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc)


def _testo(valore) -> str | None:
    if valore is None:
        return None
    testo = str(valore).strip()
    return testo or None


def riferimento_da_tabellone(voce: dict) -> RiferimentoTreno | None:
    """Una riga di partenze/arrivi -> riferimento per chiedere l'andamento."""
    numero, origine, data = voce.get("numeroTreno"), voce.get("codOrigine"), voce.get("dataPartenzaTreno")
    if not (numero and origine and data):
        return None
    return RiferimentoTreno(numero=str(numero), cod_origine=str(origine), data_partenza_ms=int(data))


def _fermata(f: dict) -> Fermata:
    return Fermata(
        codice=str(f.get("id") or ""),
        nome=str(f.get("stazione") or ""),
        arrivo_programmato=_ora(f.get("arrivo_teorico")),
        partenza_programmata=_ora(f.get("partenza_teorica")),
        arrivo_reale=_ora(f.get("arrivoReale")),
        partenza_reale=_ora(f.get("partenzaReale")),
        binario=_testo(f.get("binarioEffettivoArrivoDescrizione"))
        or _testo(f.get("binarioEffettivoPartenzaDescrizione"))
        or _testo(f.get("binarioProgrammatoArrivoDescrizione"))
        or _testo(f.get("binarioProgrammatoPartenzaDescrizione")),
        soppressa=f.get("actualFermataType") == FERMATA_SOPPRESSA,
    )


def _sigla_e_categoria(dati: dict, numero: str) -> tuple[str, str]:
    sigla = _testo(dati.get("compNumeroTreno"))
    categoria = _testo(dati.get("categoria")) or _testo(dati.get("categoriaDescrizione"))
    if sigla and " " in sigla:
        categoria = sigla.split()[0]
    categoria = categoria or "TRENO"
    return sigla or f"{categoria} {numero}", categoria


def treno_da_andamento(dati: dict, riferimento: RiferimentoTreno) -> Treno:
    sigla, categoria = _sigla_e_categoria(dati, riferimento.numero)
    fermate = [_fermata(f) for f in dati.get("fermate") or []]
    return Treno(
        riferimento=riferimento,
        categoria=categoria,
        sigla=sigla,
        origine=str(dati.get("origine") or ""),
        destinazione=str(dati.get("destinazione") or ""),
        ritardo_min=int(dati.get("ritardo") or 0),
        fermate=fermate,
        ultimo_rilevamento_luogo=_testo(dati.get("stazioneUltimoRilevamento")),
        ultimo_rilevamento_ora=_ora(dati.get("oraUltimoRilevamento")),
        soppresso=bool(fermate) and all(f.soppressa for f in fermate),
    )
