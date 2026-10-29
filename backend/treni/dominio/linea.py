"""La linea ferroviaria: stazioni in ordine di chilometrica."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Stazione:
    id: str  # identificativo breve, es. "lodi"
    nome: str  # nome mostrato sul quadro
    nome_vt: str  # nome come lo scrive ViaggiaTreno, es. "LODI"
    km: float  # progressiva chilometrica sulla linea
    binari: tuple[str, ...]  # binari disegnati sul quadro
    codice: str | None = None  # codice ViaggiaTreno, es. "S01700"


@dataclass(frozen=True)
class Linea:
    id: str
    nome: str
    descrizione: str
    stazioni: tuple[Stazione, ...]  # ordinate per km crescente
    max_salto_km: float  # oltre questa distanza tra due fermate il treno non sta su questa linea
    verso_crescente: str  # es. "verso Bologna"
    verso_decrescente: str  # es. "verso Milano"

    def stazione(self, id_stazione: str) -> Stazione:
        for s in self.stazioni:
            if s.id == id_stazione:
                return s
        raise KeyError(id_stazione)

    def stazione_piu_vicina(self, km: float) -> Stazione:
        return min(self.stazioni, key=lambda s: abs(s.km - km))
