// Disegna e muove i treni sul quadro.
// Come nei quadri RFI il numero del treno sta dentro il rettangolo ("descrittore").
// In linea il ritardo è scritto accanto; in stazione, dove i binari sono vicini,
// diventa il colore del bordo per non sovrapporsi ai treni dei binari accanto.
// Sui raccordi, per i treni in arrivo, accanto compaiono i minuti mancanti al bivio.

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

/** Dove disegnare il treno e verso quale lato dello schermo punta. */
function collocazione(p, geo, puntoRaccordo) {
  if (p.stato === "sul_raccordo") {
    const q = puntoRaccordo(p.raccordo_id, p.avanzamento, p.entrata);
    return q && { x: q.x, y: q.y, d: q.versoSchermo };
  }
  let y = geo.yCorsa(p.direzione);
  if (p.stato === "in_stazione") {
    const stazione = geo.stazione(p.stazione_id);
    y = geo.yBinari(stazione)[geo.indiceBinario(stazione, p.binario, p.direzione)];
  }
  return { x: geo.xDaKm(p.km), y, d: p.direzione };
}

function testoAccanto(treno) {
  const p = treno.posizione;
  if (p.stato === "sul_raccordo" && p.entrata && p.minuti_al_bivio != null) {
    return { testo: `tra ${p.minuti_al_bivio}'`, colore: "var(--itinerario)" };
  }
  const inRitardo = treno.ritardo > 0 && p.stato !== "in_stazione";
  return { testo: inRitardo ? `+${treno.ritardo}'` : "", colore: coloreRitardo(treno.ritardo) };
}

function aggiornaTreno(parti, treno, geo, puntoRaccordo) {
  const p = treno.posizione;
  const dove = collocazione(p, geo, puntoRaccordo);
  parti.gruppo.style.display = dove ? "" : "none";
  if (!dove) return;
  parti.gruppo.style.transform = `translate(${dove.x}px, ${dove.y}px)`;

  // Il corpo è centrato sul punto; la punta indica la direzione di marcia.
  const colore = coloreCategoria(treno.categoria);
  const d = dove.d;
  parti.corpo.setAttribute("x", -LUNGHEZZA / 2);
  parti.corpo.style.fill = colore;
  const xp = (d * LUNGHEZZA) / 2;
  parti.punta.setAttribute("points", `${xp},${-ALTEZZA / 2} ${xp + d * 7},0 ${xp},${ALTEZZA / 2}`);
  parti.punta.style.fill = colore;

  parti.sigla.setAttribute("y", 4);
  parti.sigla.textContent = treno.numero;

  const inStazione = p.stato === "in_stazione";
  const inRitardo = treno.ritardo > 0;
  const accanto = testoAccanto(treno);
  parti.ritardo.setAttribute("y", d > 0 || p.stato === "sul_raccordo" ? -10 : 20);
  parti.ritardo.textContent = accanto.testo;
  parti.ritardo.style.fill = accanto.colore;
  parti.corpo.style.stroke = inStazione && inRitardo ? coloreRitardo(treno.ritardo) : "";
  const ritardo = inRitardo ? `  +${treno.ritardo}'` : "";
  parti.titolo.textContent = `${treno.sigla}  ${treno.origine} → ${treno.destinazione}${ritardo}`;
}

export function creaLivelloTreni(livello, geo, alClic) {
  const disegnati = new Map();

  function aggiorna(treni, selezionato, puntoRaccordo) {
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
        aggiornaTreno(parti, treno, geo, puntoRaccordo);
        parti.gruppo.getBoundingClientRect();
        parti.gruppo.style.transition = "";
      } else {
        aggiornaTreno(parti, treno, geo, puntoRaccordo);
      }
      parti.gruppo.classList.toggle("selezionato", treno.chiave === selezionato);
    }
  }

  return { aggiorna };
}
