"""Un treno con le sue fermate, come arriva dalla fonte dati."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class RiferimentoTreno:
    """Quanto basta per chiedere alla fonte l'andamento di un treno."""

    numero: str
    cod_origine: str
    data_partenza_ms: int

    @property
    def chiave(self) -> str:
        return f"{self.cod_origine}-{self.numero}-{self.data_partenza_ms}"


@dataclass
class Fermata:
    codice: str
    nome: str
    arrivo_programmato: datetime | None
    partenza_programmata: datetime | None
    arrivo_reale: datetime | None = None
    partenza_reale: datetime | None = None
    binario: str | None = None
    soppressa: bool = False


@dataclass
class Treno:
    riferimento: RiferimentoTreno
    categoria: str  # es. "REG", "IC", "FR"
    sigla: str  # es. "REG 2345"
    origine: str
    destinazione: str
    ritardo_min: int
    fermate: list[Fermata] = field(default_factory=list)
    ultimo_rilevamento_luogo: str | None = None
    ultimo_rilevamento_ora: datetime | None = None
    soppresso: bool = False

    @property
    def chiave(self) -> str:
        return self.riferimento.chiave

    @property
    def numero(self) -> str:
        return self.riferimento.numero
