"""Fonte dati simulata: si comporta come ViaggiaTreno ma con treni inventati."""

from datetime import datetime, timedelta, timezone

from treni.dominio.linea import Linea, Stazione
from treni.dominio.treno import Fermata, RiferimentoTreno, Treno, VoceTabellone
from treni.linee.abbinamento import normalizza_nome
from treni.fonti.demo.orario_demo import ROMA, ServizioDemo, servizi_del_giorno

FINESTRA_FUTURO = timedelta(minutes=60)


class FonteDemo:
    """I treni simulati circolano sempre sulla linea di partenza (la prima
    ricevuta in `prepara`), anche se poi lo schermo ne mostra un'altra."""

    nome = "Demo"
    in_tempo_reale = False

    def __init__(self):
        self._servizi: dict[str, ServizioDemo] = {}
        self._linea: Linea | None = None

    async def prepara(self, linea: Linea) -> Linea:
        self._linea = self._linea or linea
        return linea

    def _servizi_attivi(self) -> list[tuple[RiferimentoTreno, ServizioDemo]]:
        if self._linea is None:
            return []
        adesso = datetime.now(timezone.utc)
        oggi = adesso.astimezone(ROMA).date()
        attivi = []
        for giorno in (oggi - timedelta(days=1), oggi):
            for s in servizi_del_giorno(self._linea, giorno):
                inizio, fine = s.orari[0][1], s.orari[-1][0]
                fine += timedelta(minutes=s.ritardo_finale_min + 5)
                if inizio - FINESTRA_FUTURO <= adesso <= fine:
                    rif = self._riferimento(s)
                    self._servizi[rif.chiave] = s
                    attivi.append((rif, s))
        return attivi

    def _riferimento(self, s: ServizioDemo) -> RiferimentoTreno:
        ms = int(s.orari[0][1].timestamp() * 1000)
        return RiferimentoTreno(numero=s.numero, cod_origine="DEMO", data_partenza_ms=ms)

    async def scopri_treni(self, linea: Linea) -> list[RiferimentoTreno]:
        return [rif for rif, _ in self._servizi_attivi()]

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

    async def cerca_stazioni(self, testo: str) -> list[tuple[str, str]]:
        cercato = normalizza_nome(testo)
        if self._linea is None:
            return []
        return [
            (s.nome_vt, f"DEMO-{s.id}")
            for s in self._linea.stazioni
            if normalizza_nome(s.nome_vt).startswith(cercato)
        ]

    async def tabellone(self, codice_stazione: str) -> list[VoceTabellone]:
        voci = []
        for rif, s in self._servizi_attivi():
            ids = [st.id for st in s.stazioni]
            id_stazione = codice_stazione.removeprefix("DEMO-")
            if id_stazione not in ids:
                continue
            i = ids.index(id_stazione)
            if i < len(ids) - 1:
                voci.append(VoceTabellone(rif, s.categoria, "partenza", s.stazioni[-1].nome_vt))
            if i > 0:
                voci.append(VoceTabellone(rif, s.categoria, "arrivo", s.stazioni[0].nome_vt))
        return voci

    async def coordinate(self, codice_stazione: str) -> tuple[float, float] | None:
        return None  # la demo ricava le distanze dai tempi di percorrenza

    async def chiudi(self) -> None:
        pass


def _binario(stazione: Stazione, numero: int) -> str:
    """Treni dispari sulla prima metà dei binari, pari sulla seconda."""
    meta = max(len(stazione.binari) // 2, 1)
    gruppo = stazione.binari[:meta] if numero % 2 else stazione.binari[meta:] or stazione.binari
    return gruppo[(numero // 2) % len(gruppo)]
