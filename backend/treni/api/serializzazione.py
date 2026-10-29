"""Trasforma gli oggetti del dominio nel JSON inviato allo schermo.

Gli orari viaggiano come millisecondi dal 1970 (UTC), comodi per JavaScript.
"""

from datetime import datetime

from treni.dominio.linea import Linea
from treni.servizi.istantanea import Istantanea, TrenoInCircolazione
from treni.servizi.registro import StatoFonte


def ms(istante: datetime | None) -> int | None:
    return int(istante.timestamp() * 1000) if istante else None


def linea_json(linea: Linea) -> dict:
    return {
        "id": linea.id,
        "nome": linea.nome,
        "descrizione": linea.descrizione,
        "verso_crescente": linea.verso_crescente,
        "verso_decrescente": linea.verso_decrescente,
        "stazioni": [
            {"id": s.id, "nome": s.nome, "km": s.km, "binari": list(s.binari)}
            for s in linea.stazioni
        ],
    }


def _prossima_fermata(t: TrenoInCircolazione, adesso: datetime) -> dict | None:
    for fermata, passaggio in zip(t.treno.fermate, t.orario):
        if passaggio.arrivo > adesso and not fermata.soppressa:
            return {"nome": fermata.nome, "ora": ms(passaggio.arrivo)}
    return None


def treno_json(t: TrenoInCircolazione, adesso: datetime) -> dict:
    p, treno = t.posizione, t.treno
    return {
        "chiave": treno.chiave,
        "sigla": treno.sigla,
        "categoria": treno.categoria,
        "numero": treno.numero,
        "origine": treno.origine,
        "destinazione": treno.destinazione,
        "ritardo": treno.ritardo_min,
        "ultimo_rilevamento": {
            "luogo": treno.ultimo_rilevamento_luogo,
            "ora": ms(treno.ultimo_rilevamento_ora),
        },
        "prossima_fermata": _prossima_fermata(t, adesso),
        "posizione": None if p is None else {
            "stato": p.stato.value,
            "km": round(p.km, 3),
            "direzione": p.direzione,
            "stazione_id": p.stazione_id,
            "binario": p.binario,
            "da_stazione_id": p.da_stazione_id,
            "a_stazione_id": p.a_stazione_id,
        },
    }


def istantanea_json(ist: Istantanea, fonte: StatoFonte) -> dict:
    return {
        "ora": ms(ist.adesso),
        "fonte": {
            "nome": fonte.nome,
            "in_tempo_reale": fonte.in_tempo_reale,
            "ok": fonte.ok,
            "messaggio": fonte.messaggio,
            "ultimo_aggiornamento": ms(fonte.ultimo_aggiornamento),
        },
        "treni": [treno_json(t, ist.adesso) for t in ist.treni],
        "incroci": [
            {
                "tipo": i.tipo.value,
                "treno_a": i.treno_a,
                "treno_b": i.treno_b,
                "km": i.km,
                "ora": ms(i.ora),
                "stazione_vicina_id": i.stazione_vicina_id,
            }
            for i in ist.incroci
        ],
    }


def dettaglio_treno_json(t: TrenoInCircolazione, adesso: datetime, stazioni_linea) -> dict:
    dati = treno_json(t, adesso)
    dati["fermate"] = [
        {
            "nome": f.nome,
            "sulla_linea": stazione is not None,
            "binario": f.binario,
            "soppressa": f.soppressa,
            "arrivo_programmato": ms(f.arrivo_programmato),
            "partenza_programmata": ms(f.partenza_programmata),
            "arrivo_reale": ms(f.arrivo_reale),
            "partenza_reale": ms(f.partenza_reale),
            "arrivo_stimato": ms(p.arrivo),
            "partenza_stimata": ms(p.partenza),
        }
        for f, p, stazione in zip(t.treno.fermate, t.orario, stazioni_linea)
    ]
    return dati
