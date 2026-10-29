"""Salva le linee in YAML ed elenca quelle disponibili in dati/linee."""

from pathlib import Path

import yaml

from treni.dominio.linea import Linea


def salva_linea(cartella: Path, linea: Linea) -> Path:
    dati = {
        "id": linea.id,
        "nome": linea.nome,
        "descrizione": linea.descrizione,
        "verso_crescente": linea.verso_crescente,
        "verso_decrescente": linea.verso_decrescente,
        "max_salto_km": linea.max_salto_km,
        "stazioni": [
            {
                "id": s.id,
                "nome": s.nome,
                "nome_vt": s.nome_vt,
                "km": s.km,
                "binari": list(s.binari),
                **({"codice": s.codice} if s.codice else {}),
            }
            for s in linea.stazioni
        ],
    }
    cartella.mkdir(parents=True, exist_ok=True)
    percorso = cartella / f"{linea.id}.yaml"
    with percorso.open("w", encoding="utf-8") as f:
        f.write("# Linea generata dalla finestra \"Scegli linea\": puoi modificarla a mano.\n")
        yaml.safe_dump(dati, f, allow_unicode=True, sort_keys=False)
    return percorso


def elenco_linee(cartella: Path) -> list[dict]:
    """[{id, nome}] di tutte le linee salvate, in ordine di nome."""
    linee = []
    for percorso in sorted(cartella.glob("*.yaml")):
        with percorso.open(encoding="utf-8") as f:
            dati = yaml.safe_load(f) or {}
        linee.append({"id": percorso.stem, "nome": dati.get("nome", percorso.stem)})
    return sorted(linee, key=lambda l: l["nome"])
