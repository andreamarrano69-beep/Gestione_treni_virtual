"""Trova i codici ViaggiaTreno delle stazioni della linea, con cache su file."""

import json
import logging
from dataclasses import replace
from pathlib import Path

from treni.dominio.linea import Linea
from treni.fonti.base import ErroreFonte
from treni.fonti.viaggiatreno.client import ClientViaggiaTreno
from treni.linee.abbinamento import normalizza_nome

log = logging.getLogger(__name__)


def _leggi_cache(percorso: Path) -> dict[str, str]:
    if percorso.exists():
        return json.loads(percorso.read_text(encoding="utf-8"))
    return {}


async def _cerca_codice(client: ClientViaggiaTreno, nome_vt: str) -> str | None:
    risultati = await client.cerca_stazione(nome_vt)
    cercato = normalizza_nome(nome_vt)
    for nome, codice in risultati:
        if normalizza_nome(nome) == cercato:
            return codice
    if risultati:
        log.warning("Nessun nome identico per %s, uso %s", nome_vt, risultati[0][0])
        return risultati[0][1]
    return None


async def risolvi_codici(linea: Linea, client: ClientViaggiaTreno, cartella_cache: Path) -> Linea:
    percorso = cartella_cache / "codici_stazioni.json"
    cache = _leggi_cache(percorso)
    stazioni = []
    for s in linea.stazioni:
        codice = s.codice or cache.get(s.nome_vt)
        if codice is None:
            try:
                codice = await _cerca_codice(client, s.nome_vt)
            except ErroreFonte as e:
                log.warning("Codice di %s non trovato: %s", s.nome_vt, e)
            if codice:
                cache[s.nome_vt] = codice
        stazioni.append(replace(s, codice=codice))

    cartella_cache.mkdir(parents=True, exist_ok=True)
    percorso.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    return replace(linea, stazioni=tuple(stazioni))
