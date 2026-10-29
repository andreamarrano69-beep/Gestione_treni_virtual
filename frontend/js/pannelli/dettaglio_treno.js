// Scheda del treno selezionato: tutte le fermate con orari programmati e reali.

import { caricaDettaglioTreno } from "../rete/api.js";
import { html } from "../util/dom.js";
import { coloreRitardo, nomeProprio, ora, testoRitardo } from "../util/formato.js";

const AGGIORNA_OGNI_MS = 15000;

function cellaOrario(programmato, reale, stimato) {
  if (!programmato && !reale) return html("td", { testo: "" });
  const effettivo = reale || stimato;
  const testo = reale ? ora(reale) : `~${ora(stimato)}`;
  const scarto = Math.round(((effettivo || 0) - (programmato || effettivo || 0)) / 60000);
  const span = html("span", { testo: `${ora(programmato)} ${testo}` });
  if (reale) span.style.color = coloreRitardo(scarto);
  return html("td", {}, [span]);
}

function rigaFermata(f, adesso) {
  const passata = (f.partenza_reale || f.arrivo_reale) && (f.partenza_stimata || 0) < adesso;
  const nome = f.sulla_linea ? html("strong", { testo: nomeProprio(f.nome) }) : nomeProprio(f.nome);
  return html("tr", { class: passata ? "passata" : "" }, [
    html("td", {}, [nome, f.soppressa ? " (soppressa)" : ""]),
    cellaOrario(f.arrivo_programmato, f.arrivo_reale, f.arrivo_stimato),
    cellaOrario(f.partenza_programmata, f.partenza_reale, f.partenza_stimata),
    html("td", { testo: f.binario || "" }),
  ]);
}

function disegna(contenitore, dati) {
  const ritardo = html("span", { class: "ritardo", testo: testoRitardo(dati.ritardo) });
  ritardo.style.color = coloreRitardo(dati.ritardo);
  const rilevamento = dati.ultimo_rilevamento.luogo
    ? `Ultimo rilevamento: ${nomeProprio(dati.ultimo_rilevamento.luogo)} alle ${ora(dati.ultimo_rilevamento.ora)}`
    : "";
  contenitore.replaceChildren(
    html("div", { class: "dettaglio__intestazione" }, [
      html("strong", { testo: dati.sigla }), " ", ritardo,
      html("div", { testo: `${nomeProprio(dati.origine)} → ${nomeProprio(dati.destinazione)}` }),
      html("div", { class: "vuoto", testo: rilevamento }),
    ]),
    html("table", { class: "tabella" }, [
      html("thead", {}, [html("tr", {}, ["Fermata", "Arrivo", "Partenza", "Bin."].map((t) => html("th", { testo: t })))]),
      html("tbody", {}, dati.fermate.map((f) => rigaFermata(f, Date.now()))),
    ]),
  );
}

export function creaDettaglioTreno() {
  const contenitore = document.getElementById("dettaglio-treno");
  let chiaveAttuale = null;
  let timer = null;

  async function carica() {
    const chiave = chiaveAttuale;
    try {
      const dati = await caricaDettaglioTreno(chiave);
      if (chiave === chiaveAttuale) disegna(contenitore, dati);
    } catch {
      if (chiave === chiaveAttuale) {
        contenitore.replaceChildren(html("p", { class: "vuoto", testo: "Treno non più seguito." }));
      }
    }
  }

  function mostra(chiave) {
    chiaveAttuale = chiave;
    clearInterval(timer);
    carica();
    timer = setInterval(carica, AGGIORNA_OGNI_MS);
  }
  return { mostra };
}
