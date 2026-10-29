"""Costruisce una linea dalle fermate reali dei treni che la percorrono.

Tra i treni verso la destinazione scelta si prende quello con più fermate
(di solito un regionale): le sue fermate diventano le stazioni della linea.
"""

import re

from treni.dominio.linea import Linea, Stazione
from treni.dominio.treno import Fermata, VoceTabellone
from treni.fonti.base import ErroreFonte, FonteDati
from treni.linee.abbinamento import normalizza_nome
from treni.servizi.distanze import progressive_km

MASSIMO_CANDIDATI = 5
CATEGORIE_CAPILLARI = ("REG", "R", "RV", "S", "MET", "RE")  # treni che fermano ovunque


def _identificativo(testo: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", testo.lower()).strip("_")


def nome_leggibile(testo: str) -> str:
    return " ".join(p.capitalize() for p in testo.split())


def _tratto(fermate: list[Fermata], voce: VoceTabellone, codice: str, nome: str) -> list[Fermata]:
    """Le fermate dalla stazione scelta verso il capolinea."""
    cercato = normalizza_nome(nome)
    indice = next(
        (i for i, f in enumerate(fermate) if f.codice == codice or normalizza_nome(f.nome) == cercato),
        None,
    )
    if indice is None:
        return []
    tratto = fermate[indice:] if voce.verso == "partenza" else fermate[: indice + 1][::-1]
    return [f for f in tratto if not f.soppressa]


def _candidati(voci: list[VoceTabellone]) -> list[VoceTabellone]:
    capillari = [v for v in voci if v.categoria in CATEGORIE_CAPILLARI]
    altri = [v for v in voci if v.categoria not in CATEGORIE_CAPILLARI]
    return (capillari + altri)[:MASSIMO_CANDIDATI]


def _binari_visti(tratti: list[list[Fermata]]) -> dict[str, set[str]]:
    visti: dict[str, set[str]] = {}
    for tratto in tratti:
        for f in tratto:
            if f.binario:
                visti.setdefault(normalizza_nome(f.nome), set()).add(f.binario)
    return visti


def _ordina_binari(binari: set[str]) -> tuple[str, ...]:
    tutti = binari | {"1", "2"}
    return tuple(sorted(tutti, key=lambda b: (len(b), b))[:8])


async def costruisci_linea(
    fonte: FonteDati, codice: str, nome: str, capolinea: str, voci: list[VoceTabellone]
) -> Linea:
    tratti = []
    for voce in _candidati(voci):
        treno = await fonte.andamento(voce.riferimento)
        if treno:
            tratti.append(_tratto(treno.fermate, voce, codice, nome))
    tratti = [t for t in tratti if len(t) >= 2]
    if not tratti:
        raise ErroreFonte(f"Nessun treno utile per costruire la linea verso {capolinea}")

    scelto = max(tratti, key=len)
    km = await progressive_km(fonte, scelto)
    binari = _binari_visti(tratti)
    stazioni, usati = [], set()
    for fermata, progressiva in zip(scelto, km):
        identificativo = _identificativo(fermata.nome)
        while identificativo in usati:
            identificativo += "_"
        usati.add(identificativo)
        stazioni.append(Stazione(
            id=identificativo,
            nome=nome_leggibile(fermata.nome),
            nome_vt=fermata.nome,
            km=progressiva,
            binari=_ordina_binari(binari.get(normalizza_nome(fermata.nome), set())),
            codice=fermata.codice or None,
        ))

    partenza, arrivo = nome_leggibile(scelto[0].nome), nome_leggibile(scelto[-1].nome)
    return Linea(
        id=_identificativo(f"{partenza}_{arrivo}"),
        nome=f"{partenza} – {arrivo}",
        descrizione=f"Ricavata dalle fermate reali dei treni · {len(scelto)} stazioni · km approssimati",
        stazioni=tuple(stazioni),
        max_salto_km=80,
        verso_crescente=f"verso {arrivo}",
        verso_decrescente=f"verso {partenza}",
    )
