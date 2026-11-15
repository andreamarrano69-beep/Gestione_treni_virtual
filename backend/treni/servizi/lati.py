"""Da quale estremità di una stazione un treno entra o esce dalla linea.

"sinistra" è il lato dei km minori, "destra" quello dei km maggiori. Un treno
che dopo l'entrata va verso km crescenti è entrato da sinistra; uno che esce
andando verso km crescenti esce da destra.
"""

from treni.dominio.linea import Linea, Stazione

SINISTRA = "sinistra"
DESTRA = "destra"


def lato_e_direzione(linea: Linea, stazione: Stazione, entrata: bool, direzione: int | None) -> tuple[str, int]:
    """direzione: verso di marcia sulla linea, o None se il treno tocca solo questa stazione."""
    if direzione is not None:
        if entrata:
            return (SINISTRA if direzione > 0 else DESTRA), direzione
        return (DESTRA if direzione > 0 else SINISTRA), direzione
    # Treno che tocca la linea in una sola stazione: nei capolinea arriva e
    # riparte dal lato esterno, nelle stazioni intermedie la attraversa.
    if stazione.id == linea.stazioni[0].id:
        return SINISTRA, (1 if entrata else -1)
    if stazione.id == linea.stazioni[-1].id:
        return DESTRA, (-1 if entrata else 1)
    return (SINISTRA if entrata else DESTRA), 1
