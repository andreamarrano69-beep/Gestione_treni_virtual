"""Legge la descrizione di una linea da un file YAML in dati/linee."""

from pathlib import Path

import yaml

from treni.dominio.linea import Linea, Stazione


def carica_linea(cartella: Path, id_linea: str) -> Linea:
    percorso = cartella / f"{id_linea}.yaml"
    with percorso.open(encoding="utf-8") as f:
        dati = yaml.safe_load(f)

    stazioni = tuple(
        sorted(
            (
                Stazione(
                    id=s["id"],
                    nome=s["nome"],
                    nome_vt=s["nome_vt"],
                    km=float(s["km"]),
                    binari=tuple(str(b) for b in s.get("binari", ["1", "2"])),
                    codice=s.get("codice"),
                )
                for s in dati["stazioni"]
            ),
            key=lambda s: s.km,
        )
    )
    return Linea(
        id=dati["id"],
        nome=dati["nome"],
        descrizione=dati.get("descrizione", ""),
        stazioni=stazioni,
        max_salto_km=float(dati.get("max_salto_km", 80)),
        verso_crescente=dati.get("verso_crescente", "km crescenti"),
        verso_decrescente=dati.get("verso_decrescente", "km decrescenti"),
    )
