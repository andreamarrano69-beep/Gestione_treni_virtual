"""I tipi di treno della demo: orari cadenzati sulla Milano–Bologna, più
treni che arrivano da altre linee o dall'estero e ne escono."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TipoServizio:
    categoria: str
    da: str  # id della prima stazione sulla linea (nel verso dei km crescenti)
    a: str  # id dell'ultima stazione sulla linea
    fermate: tuple[str, ...] | None  # None = ferma ovunque tra da e a
    cadenza_min: int
    scostamento_min: int  # minuto della prima partenza
    velocita_kmh: float
    sosta_min: float
    base_numero: int
    # Fermate fuori linea prima di `da` (con i minuti fino alla fermata seguente)
    # e dopo `a` (con i minuti dalla fermata precedente).
    prima: tuple[tuple[str, int], ...] = ()
    dopo: tuple[tuple[str, int], ...] = ()


_PRINCIPALI_RV = ("milano_c", "rogoredo", "lodi", "codogno", "piacenza", "fidenza",
                  "parma", "reggio_e", "modena", "bologna_c")
_PRINCIPALI_IC = ("milano_c", "rogoredo", "piacenza", "parma", "reggio_e", "modena", "bologna_c")

TIPI = (
    TipoServizio("REG", "milano_c", "piacenza", None, 30, 5, 70, 1, 2600),
    TipoServizio("REG", "piacenza", "bologna_c", None, 30, 20, 75, 1, 3900),
    TipoServizio("RV", "milano_c", "bologna_c", _PRINCIPALI_RV, 60, 25, 100, 2, 2100),
    TipoServizio("IC", "milano_c", "bologna_c", _PRINCIPALI_IC, 120, 50, 125, 2, 600),
    # Milano – Pavia: esce dalla linea a Rogoredo.
    TipoServizio("REG", "milano_c", "rogoredo", ("milano_c", "rogoredo"), 30, 12, 70, 1, 10400,
                 dopo=(("LOCATE TRIULZI", 9), ("PAVIA", 16))),
    # Milano – Cremona: esce a Codogno.
    TipoServizio("REG", "milano_c", "codogno", ("milano_c", "rogoredo", "lodi", "codogno"), 60, 40, 85, 1, 10800,
                 dopo=(("MALEO", 9), ("CREMONA", 18))),
    # Zurigo – Milano: tocca solo il capolinea di Milano Centrale.
    TipoServizio("EC", "milano_c", "milano_c", None, 120, 35, 100, 0, 310,
                 prima=(("ZURICH HB", 35), ("ARTH-GOLDAU", 70), ("LUGANO", 25), ("CHIASSO", 10),
                        ("COMO S.GIOVANNI", 25), ("MONZA", 12))),
    # Bologna – Monaco di Baviera: tocca solo il capolinea di Bologna.
    TipoServizio("EC", "bologna_c", "bologna_c", None, 240, 15, 100, 0, 84,
                 dopo=(("VERONA PORTA NUOVA", 55), ("TRENTO", 55), ("BOLZANO", 35),
                       ("BRENNERO", 65), ("INNSBRUCK HBF", 40), ("MUENCHEN HBF", 110))),
)
