// Disegna e muove i treni sul quadro.
// Come nei quadri RFI il numero del treno sta dentro il rettangolo ("descrittore").
// In linea il ritardo è scritto accanto; in stazione, dove i binari sono vicini,
// diventa il colore del bordo per non sovrapporsi ai treni dei binari accanto.

import { svg } from "../util/dom.js";
import { coloreCategoria, coloreRitardo } from "../util/formato.js";

const LUNGHEZZA = 40;
const ALTEZZA = 13;

function creaTreno(treno, alClic) {
  const gruppo = svg("g", { class: "treno" });
  const corpo = svg("rect", { class: "treno__corpo", y: -ALTEZZA / 2, width: LUNGHEZZA, height: ALTEZZA, rx: 2 });
  const punta = svg("polygon", { class: "treno__corpo" });
  const sigla = svg("text", { class: "treno__sigla", "text-anchor": "middle" });
  const ritardo = svg("text", { class: "treno__ritardo", "text-anchor": "middle" });
  const titolo = svg("title");
  gruppo.append(corpo, punta, sigla, ritardo, titolo);
  gruppo.addEventListener("click", () => alClic(treno.chiave));
  return { gruppo, corpo, punta, sigla, ritardo, titolo };
}

function aggiornaTreno(parti, treno, geo) {
  const p = treno.posizione;
  const x = geo.xDaKm(p.km);
  let y = geo.yCorsa(p.direzione);
  if (p.stato === "in_stazione") {
    const stazione = geo.stazione(p.stazione_id);
    y = geo.yBinari(stazione)[geo.indiceBinario(stazione, p.binario, p.direzione)];
  }
  parti.gruppo.style.transform = `translate(${x}px, ${y}px)`;

  // Il corpo è centrato sul punto; la punta indica la direzione di marcia.
  const colore = coloreCategoria(treno.categoria);
  const d = p.direzione;
  parti.corpo.setAttribute("x", -LUNGHEZZA / 2);
  parti.corpo.style.fill = colore;
  const xp = (d * LUNGHEZZA) / 2;
  parti.punta.setAttribute("points", `${xp},${-ALTEZZA / 2} ${xp + d * 7},0 ${xp},${ALTEZZA / 2}`);
  parti.punta.style.fill = colore;

  parti.sigla.setAttribute("y", 4);
  parti.sigla.textContent = treno.numero;

  const inStazione = p.stato === "in_stazione";
  const inRitardo = treno.ritardo > 0;
  parti.ritardo.setAttribute("y", d > 0 ? -10 : 20);
  parti.ritardo.textContent = inRitardo && !inStazione ? `+${treno.ritardo}'` : "";
  parti.ritardo.style.fill = coloreRitardo(treno.ritardo);
  parti.corpo.style.stroke = inStazione && inRitardo ? coloreRitardo(treno.ritardo) : "";
  const ritardo = inRitardo ? `  +${treno.ritardo}'` : "";
  parti.titolo.textContent = `${treno.sigla}  ${treno.origine} → ${treno.destinazione}${ritardo}`;
}

export function creaLivelloTreni(livello, geo, alClic) {
  const disegnati = new Map();

  function aggiorna(treni, selezionato) {
    const visibili = treni.filter((t) => t.posizione);
    const presenti = new Set(visibili.map((t) => t.chiave));
    for (const [chiave, parti] of disegnati) {
      if (!presenti.has(chiave)) {
        parti.gruppo.remove();
        disegnati.delete(chiave);
      }
    }
    for (const treno of visibili) {
      let parti = disegnati.get(treno.chiave);
      if (!parti) {
        parti = creaTreno(treno, alClic);
        disegnati.set(treno.chiave, parti);
        livello.append(parti.gruppo);
        parti.gruppo.style.transition = "none"; // il primo posizionamento non va animato
        aggiornaTreno(parti, treno, geo);
        parti.gruppo.getBoundingClientRect();
        parti.gruppo.style.transition = "";
      } else {
        aggiornaTreno(parti, treno, geo);
      }
      parti.gruppo.classList.toggle("selezionato", treno.chiave === selezionato);
    }
  }

  return { aggiorna };
}
