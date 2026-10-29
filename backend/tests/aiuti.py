"""Costruttori di dati di prova condivisi dai test."""

from datetime import datetime, timedelta, timezone

from treni.dominio.linea import Linea, Stazione
from treni.dominio.treno import Fermata, RiferimentoTreno, Treno

INIZIO = datetime(2026, 10, 29, 9, 0, tzinfo=timezone.utc)


def minuti(m: float) -> datetime:
    return INIZIO + timedelta(minutes=m)


def linea_prova() -> Linea:
    stazioni = tuple(
        Stazione(id=n.lower(), nome=n, nome_vt=n.upper(), km=km, binari=("1", "2", "3"))
        for n, km in [("Alfa", 0), ("Beta", 10), ("Gamma", 30), ("Delta", 40)]
    )
    return Linea(
        id="prova", nome="Prova", descrizione="", stazioni=stazioni,
        max_salto_km=25, verso_crescente="verso Delta", verso_decrescente="verso Alfa",
    )


def treno_prova(numero: str, fermate: list[tuple[str, float | None, float | None]], ritardo=0) -> Treno:
    """fermate: (nome, arrivo programmato in minuti, partenza programmata in minuti)."""
    return Treno(
        riferimento=RiferimentoTreno(numero=numero, cod_origine="S0", data_partenza_ms=0),
        categoria="REG",
        sigla=f"REG {numero}",
        origine=fermate[0][0],
        destinazione=fermate[-1][0],
        ritardo_min=ritardo,
        fermate=[
            Fermata(
                codice="",
                nome=nome.upper(),
                arrivo_programmato=minuti(arr) if arr is not None else None,
                partenza_programmata=minuti(par) if par is not None else None,
                binario="2",
            )
            for nome, arr, par in fermate
        ],
    )
