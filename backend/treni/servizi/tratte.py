"""Le destinazioni raggiungibili da una stazione, lette dal suo tabellone.

Un treno in arrivo da X conta come tratta verso X: la linea è la stessa,
percorsa nel verso opposto.
"""

from dataclasses import dataclass, field

from treni.dominio.treno import VoceTabellone
from treni.fonti.base import FonteDati
from treni.linee.abbinamento import normalizza_nome


@dataclass
class Destinazione:
    capolinea: str
    voci: list[VoceTabellone] = field(default_factory=list)

    @property
    def categorie(self) -> list[str]:
        return sorted({v.categoria for v in self.voci})


async def destinazioni(fonte: FonteDati, codice_stazione: str, nome_stazione: str) -> list[Destinazione]:
    gruppi: dict[str, Destinazione] = {}
    stazione = normalizza_nome(nome_stazione)
    for voce in await fonte.tabellone(codice_stazione):
        chiave = normalizza_nome(voce.capolinea)
        if not chiave or chiave == stazione:
            continue
        gruppi.setdefault(chiave, Destinazione(capolinea=voce.capolinea)).voci.append(voce)
    return sorted(gruppi.values(), key=lambda d: (-len(d.voci), d.capolinea))
