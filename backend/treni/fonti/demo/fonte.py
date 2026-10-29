"""Fonte dati simulata: si comporta come ViaggiaTreno ma con treni inventati."""

from datetime import datetime, timedelta, timezone

from treni.dominio.linea import Linea, Stazione
from treni.dominio.treno import Fermata, RiferimentoTreno, Treno
from treni.fonti.demo.orario_demo import ROMA, ServizioDemo, servizi_del_giorno

FINESTRA_FUTURO = timedelta(minutes=60)


class FonteDemo:
    nome = "Demo"
    in_tempo_reale = False

    def __init__(self):
        self._servizi: dict[str, ServizioDemo] = {}
        self._linea: Linea | None = None

    async def prepara(self, linea: Linea) -> Linea:
        self._linea = linea
        return linea

    def _riferimento(self, s: ServizioDemo) -> RiferimentoTreno:
        ms = int(s.orari[0][1].timestamp() * 1000)
        return RiferimentoTreno(numero=s.numero, cod_origine="DEMO", data_partenza_ms=ms)

    async def scopri_treni(self, linea: Linea) -> list[RiferimentoTreno]:
        adesso = datetime.now(timezone.utc)
        oggi = adesso.astimezone(ROMA).date()
        trovati = []
        for giorno in (oggi - timedelta(days=1), oggi):
            for s in servizi_del_giorno(linea, giorno):
                inizio, fine = s.orari[0][1], s.orari[-1][0]
                fine += timedelta(minutes=s.ritardo_finale_min + 5)
                if inizio - FINESTRA_FUTURO <= adesso <= fine:
                    rif = self._riferimento(s)
                    self._servizi[rif.chiave] = s
                    trovati.append(rif)
        return trovati

    async def andamento(self, riferimento: RiferimentoTreno) -> Treno | None:
        servizio = self._servizi.get(riferimento.chiave)
        if servizio is None:
            return None
        adesso = datetime.now(timezone.utc)
        fermate, ritardo_attuale = [], 0
        n = len(servizio.stazioni)
        for i, (stazione, (arrivo, partenza)) in enumerate(zip(servizio.stazioni, servizio.orari)):
            ritardo = timedelta(minutes=round(servizio.ritardo_finale_min * i / max(n - 1, 1)))
            arrivo_reale = arrivo + ritardo if i > 0 and arrivo + ritardo <= adesso else None
            partenza_reale = partenza + ritardo if i < n - 1 and partenza + ritardo <= adesso else None
            if arrivo_reale or partenza_reale:
                ritardo_attuale = int(ritardo.total_seconds() // 60)
            fermate.append(Fermata(
                codice=f"DEMO-{stazione.id}",
                nome=stazione.nome_vt,
                arrivo_programmato=None if i == 0 else arrivo,
                partenza_programmata=None if i == n - 1 else partenza,
                arrivo_reale=arrivo_reale,
                partenza_reale=partenza_reale,
                binario=_binario(stazione, int(servizio.numero)),
            ))
        return Treno(
            riferimento=riferimento,
            categoria=servizio.categoria,
            sigla=f"{servizio.categoria} {servizio.numero}",
            origine=servizio.stazioni[0].nome_vt,
            destinazione=servizio.stazioni[-1].nome_vt,
            ritardo_min=ritardo_attuale,
            fermate=fermate,
        )

    async def chiudi(self) -> None:
        pass


def _binario(stazione: Stazione, numero: int) -> str:
    """Treni dispari sulla prima metà dei binari, pari sulla seconda."""
    meta = max(len(stazione.binari) // 2, 1)
    gruppo = stazione.binari[:meta] if numero % 2 else stazione.binari[meta:] or stazione.binari
    return gruppo[(numero // 2) % len(gruppo)]
