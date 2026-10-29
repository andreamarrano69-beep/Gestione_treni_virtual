// Disegno fisso della linea: binari di corsa, fasci di stazione, deviatoi, nomi.
// Restituisce i riferimenti agli elementi da accendere quando sono occupati.

import { svg } from "../util/dom.js";
import { SEMI_STAZIONE, Y_CRESCENTE, Y_DECRESCENTE, ZONA_DEVIATOI } from "./geometria.js";

const MEZZERIA = (Y_CRESCENTE + Y_DECRESCENTE) / 2;
const Y_KM = Y_DECRESCENTE + 90; // sotto le etichette dei treni

function linea(x1, y1, x2, y2, classe) {
  return svg("line", { x1, y1, x2, y2, class: classe });
}

/** Tratti di piena linea tra due stazioni consecutive, uno per binario di corsa. */
function disegnaTratti(livello, geo, stazioni, elementi) {
  for (let i = 0; i + 1 < stazioni.length; i++) {
    const da = geo.xStazione(stazioni[i].id) + SEMI_STAZIONE + ZONA_DEVIATOI;
    const a = geo.xStazione(stazioni[i + 1].id) - SEMI_STAZIONE - ZONA_DEVIATOI;
    for (const direzione of [1, -1]) {
      const tratto = linea(da, geo.yCorsa(direzione), a, geo.yCorsa(direzione), "binario");
      elementi.tratti.set(`${stazioni[i].id}|${direzione}`, tratto);
      livello.append(tratto);
    }
  }
}

function disegnaStazione(livello, geo, stazione, elementi) {
  const x = geo.xStazione(stazione.id);
  const ys = geo.yBinari(stazione);
  const sinistra = x - SEMI_STAZIONE;
  const destra = x + SEMI_STAZIONE;
  const gruppo = svg("g", { class: "stazione" });

  gruppo.append(svg("rect", {
    x: sinistra - ZONA_DEVIATOI - 4, y: Math.min(...ys) - 12,
    width: 2 * (SEMI_STAZIONE + ZONA_DEVIATOI + 4), height: Math.max(...ys) - Math.min(...ys) + 24,
    class: "stazione__riquadro",
  }));

  ys.forEach((y, j) => {
    const yCorsa = y <= MEZZERIA ? Y_CRESCENTE : Y_DECRESCENTE;
    const binario = linea(sinistra, y, destra, y, "binario binario--stazione");
    const deviatoi = [
      linea(sinistra - ZONA_DEVIATOI, yCorsa, sinistra, y, "deviatoio"),
      linea(destra, y, destra + ZONA_DEVIATOI, yCorsa, "deviatoio"),
    ];
    elementi.binari.set(`${stazione.id}|${j}`, { binario, deviatoi });
    const etichetta = svg("text", { x: sinistra + 1, y: y - 2, class: "stazione__binario" });
    etichetta.textContent = stazione.binari[j];
    gruppo.append(...deviatoi, binario, etichetta);
  });

  const nome = svg("text", {
    x, y: Math.min(...ys) - 22, class: "stazione__nome",
    transform: `rotate(-30 ${x} ${Math.min(...ys) - 22})`,
  });
  nome.textContent = stazione.nome;
  const km = svg("text", { x, y: Y_KM, class: "stazione__km", "text-anchor": "middle" });
  km.textContent = `km ${stazione.km}`;
  gruppo.append(nome, km);
  livello.append(gruppo);
}

function disegnaVersi(livello, geo, lineaDati, stazioni) {
  const xFine = geo.xStazione(stazioni[stazioni.length - 1].id) + 40;
  const xInizio = geo.xStazione(stazioni[0].id) - 40;
  const crescente = svg("text", { x: xFine, y: Y_CRESCENTE + 4, class: "verso" });
  crescente.textContent = "▶";
  const decrescente = svg("text", { x: xInizio, y: Y_DECRESCENTE + 4, class: "verso", "text-anchor": "end" });
  decrescente.textContent = "◀";
  crescente.append(svg("title", {}, [lineaDati.verso_crescente]));
  decrescente.append(svg("title", {}, [lineaDati.verso_decrescente]));
  livello.append(crescente, decrescente);
}

export function disegnaRete(livello, geo, lineaDati) {
  const elementi = { tratti: new Map(), binari: new Map() };
  disegnaTratti(livello, geo, lineaDati.stazioni, elementi);
  for (const stazione of lineaDati.stazioni) disegnaStazione(livello, geo, stazione, elementi);
  disegnaVersi(livello, geo, lineaDati, lineaDati.stazioni);
  return elementi;
}
