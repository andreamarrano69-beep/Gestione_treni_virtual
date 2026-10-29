"""Riconosce quali fermate di un treno sono stazioni della linea."""

import re

from treni.dominio.linea import Linea, Stazione
from treni.dominio.treno import Fermata


def normalizza_nome(nome: str) -> str:
    """'Reggio-Emilia ' -> 'REGGIO EMILIA', per confronti robusti tra nomi."""
    return re.sub(r"[^A-Z0-9]+", " ", nome.upper()).strip()


class Abbinatore:
    def __init__(self, linea: Linea):
        self._per_codice = {s.codice: s for s in linea.stazioni if s.codice}
        self._per_nome = {normalizza_nome(s.nome_vt): s for s in linea.stazioni}

    def stazione_di(self, fermata: Fermata) -> Stazione | None:
        stazione = self._per_codice.get(fermata.codice)
        if stazione is None:
            stazione = self._per_nome.get(normalizza_nome(fermata.nome))
        return stazione
