// Tabella dei treni seguiti, ordinati per posizione sulla linea.

import { html } from "../util/dom.js";
import { coloreCategoria, coloreRitardo, nomeProprio, ora, testoRitardo } from "../util/formato.js";

const INTESTAZIONE = ["Treno", "Relazione", "Posizione", "Prossima fermata", "Ritardo"];

function descriviPosizione(treno, nomeStazione, nomeRaccordo) {
  const p = treno.posizione;
  if (!p) return "fuori dalla linea";
  if (p.stato === "sul_raccordo") {
    const altra = nomeProprio(nomeRaccordo(p.raccordo_id));
    return p.entrata
      ? `da ${altra}, entra a ${nomeStazione(p.stazione_id)} tra ${p.minuti_al_bivio}'`
      : `uscito a ${nomeStazione(p.stazione_id)} verso ${altra}`;
  }
  if (p.stato === "in_stazione") {
    return `a ${nomeStazione(p.stazione_id)}${p.binario ? `, bin. ${p.binario}` : ""}`;
  }
  return `tra ${nomeStazione(p.da_stazione_id)} e ${nomeStazione(p.a_stazione_id)}`;
}

function riga(treno, nomeStazione, nomeRaccordo, selezionato, alClic) {
  const categoria = html("span", { class: "categoria", testo: treno.categoria });
  categoria.style.background = coloreCategoria(treno.categoria);
  const ritardo = html("span", { class: "ritardo", testo: testoRitardo(treno.ritardo) });
  ritardo.style.color = coloreRitardo(treno.ritardo);
  const prossima = treno.prossima_fermata
    ? `${nomeProprio(treno.prossima_fermata.nome)} ${ora(treno.prossima_fermata.ora)}`
    : "—";

  const fuori = !treno.posizione || treno.posizione.stato === "sul_raccordo";
  const classi = [treno.chiave === selezionato ? "selezionato" : "", fuori ? "fuori-linea" : ""];
  const tr = html("tr", { class: classi.join(" ").trim() }, [
    html("td", {}, [categoria, ` ${treno.numero}`]),
    html("td", { testo: `${nomeProprio(treno.origine)} → ${nomeProprio(treno.destinazione)}` }),
    html("td", { testo: descriviPosizione(treno, nomeStazione, nomeRaccordo) }),
    html("td", { testo: prossima }),
    html("td", {}, [ritardo]),
  ]);
  tr.addEventListener("click", () => alClic(treno.chiave));
  return tr;
}

export function creaElencoTreni(lineaDati, alClic) {
  const tabella = document.getElementById("tabella-treni");
  const contatore = document.getElementById("contatore-treni");
  const nomi = new Map(lineaDati.stazioni.map((s) => [s.id, s.nome]));
  const nomeStazione = (id) => nomi.get(id) || id;

  function aggiorna(treni, selezionato, raccordi = []) {
    const nomiRaccordi = new Map(raccordi.map((r) => [r.id, r.nome]));
    const nomeRaccordo = (id) => nomiRaccordi.get(id) || "";
    // Prima quelli sulla linea (per km), poi quelli in arrivo da fuori.
    const ordinati = [...treni].sort(
      (a, b) => (a.posizione ? a.posizione.km : 1e9) - (b.posizione ? b.posizione.km : 1e9),
    );
    const stati = treni.map((t) => t.posizione?.stato);
    const sullaLinea = stati.filter((s) => s === "in_linea" || s === "in_stazione").length;
    const raccordo = stati.filter((s) => s === "sul_raccordo").length;
    const lontani = treni.length - sullaLinea - raccordo;
    contatore.textContent = `(${sullaLinea} sulla linea, ${raccordo} sui raccordi, ${lontani} lontani)`;
    tabella.replaceChildren(
      html("thead", {}, [html("tr", {}, INTESTAZIONE.map((t) => html("th", { testo: t })))]),
      html("tbody", {}, ordinati.map((t) => riga(t, nomeStazione, nomeRaccordo, selezionato, alClic))),
    );
  }
  return { aggiorna };
}
