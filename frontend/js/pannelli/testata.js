// Barra in alto: nome della linea, orologio e stato della fonte dati.

import { html } from "../util/dom.js";
import { oraConSecondi } from "../util/formato.js";

export function mostraLinea(lineaDati) {
  document.getElementById("nome-linea").textContent = lineaDati.nome;
  document.getElementById("descrizione-linea").textContent = lineaDati.descrizione;
  document.title = `Quadro Sinottico ${lineaDati.nome}`;
}

export function avviaOrologio() {
  const elemento = document.getElementById("orologio");
  const scrivi = () => (elemento.textContent = oraConSecondi(Date.now()));
  scrivi();
  setInterval(scrivi, 1000);
}

export function mostraStatoFonte(fonte) {
  const elemento = document.getElementById("stato-fonte");
  let tipo = fonte.in_tempo_reale ? "live" : "demo";
  let titolo = fonte.in_tempo_reale ? `LIVE · ${fonte.nome}` : "DEMO · treni simulati";
  if (!fonte.ok) tipo = "errore";
  elemento.className = `stato-fonte stato-fonte--${tipo}`;

  const dettaglio = fonte.ultimo_aggiornamento
    ? `${fonte.messaggio} · agg. ${oraConSecondi(fonte.ultimo_aggiornamento)}`
    : fonte.messaggio;
  elemento.replaceChildren(
    html("div", { class: "stato-fonte__titolo" }, [html("span", { class: "stato-fonte__punto" }), titolo]),
    html("div", { class: "stato-fonte__messaggio", testo: dettaglio }),
  );
}

export function mostraConnessionePersa() {
  mostraStatoFonte({ ok: false, nome: "", in_tempo_reale: true, messaggio: "Connessione al server persa, riprovo…" });
}
