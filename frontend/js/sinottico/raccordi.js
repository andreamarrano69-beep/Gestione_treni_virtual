// Raccordi: rami che escono dalle stazioni verso le altre linee (o l'estero).
//
// Ogni ramo scende dal bivio con una diagonale (il deviatoio) e prosegue con un
// tronco orizzontale verso l'esterno, con il nome della prima fermata fuori linea.
// I tronchi sono disposti su più file, così quelli di stazioni vicine non si coprono.

import { svg } from "../util/dom.js";
import { nomeProprio } from "../util/formato.js";
import { SEMI_STAZIONE, Y_DECRESCENTE, ZONA_DEVIATOI } from "./geometria.js";

export const Y_PRIMA_FILA = 350;
export const PASSO_FILE = 24;
const MASSIMO_FILE = 8;
const GOMITO = 20; // spostamento orizzontale della diagonale
const TRONCO = 96;
const MARGINE = 8;
const LETTERE_ETICHETTA = 15;

function disponi(raccordi, geo) {
  const file = []; // per ogni fila, gli intervalli orizzontali già occupati
  const disposti = new Map();
  const ordinati = [...raccordi].sort((a, b) => geo.xStazione(a.stazione_id) - geo.xStazione(b.stazione_id));
  for (const r of ordinati) {
    const verso = r.lato === "sinistra" ? -1 : 1;
    const xBivio = geo.xStazione(r.stazione_id) + verso * (SEMI_STAZIONE + ZONA_DEVIATOI);
    const xFine = xBivio + verso * (GOMITO + TRONCO);
    const [da, a] = [Math.min(xBivio, xFine) - MARGINE, Math.max(xBivio, xFine) + MARGINE];
    let fila = file.findIndex((occupati) => occupati.every(([x1, x2]) => a < x1 || da > x2));
    if (fila < 0) fila = Math.min(file.length, MASSIMO_FILE - 1);
    (file[fila] ||= []).push([da, a]);
    const y = Y_PRIMA_FILA + fila * PASSO_FILE;
    // Dal fondo del raccordo verso il bivio: avanzamento 1 → 0.
    const punti = [[xFine, y], [xBivio + verso * GOMITO, y], [xBivio, Y_DECRESCENTE]];
    disposti.set(r.id, { raccordo: r, verso, punti });
  }
  return { disposti, file: file.length };
}

function disegna(livello, disposti) {
  const elementi = new Map();
  for (const [id, { raccordo, verso, punti }] of disposti) {
    const [fine, gomito, bivio] = punti;
    const tronco = svg("line", { x1: fine[0], y1: fine[1], x2: gomito[0], y2: gomito[1], class: "binario raccordo" });
    const deviatoio = svg("line", { x1: gomito[0], y1: gomito[1], x2: bivio[0], y2: bivio[1], class: "deviatoio" });
    const nome = nomeProprio(raccordo.nome);
    const breve = nome.length > LETTERE_ETICHETTA ? `${nome.slice(0, LETTERE_ETICHETTA - 1)}…` : nome;
    const etichetta = svg("text", {
      x: fine[0], y: fine[1] - 4, class: "raccordo__nome", "text-anchor": verso < 0 ? "start" : "end",
    });
    etichetta.textContent = verso < 0 ? `◂ ${breve}` : `${breve} ▸`;
    etichetta.append(svg("title", {}, [`Raccordo verso ${nome}`]));
    livello.append(tronco, deviatoio, etichetta);
    elementi.set(id, { tronco, deviatoio });
  }
  return elementi;
}

function puntoLungo(punti, avanzamento) {
  const tratti = punti.slice(1).map((p, i) => Math.hypot(p[0] - punti[i][0], p[1] - punti[i][1]));
  let resto = (1 - avanzamento) * tratti.reduce((s, l) => s + l, 0);
  for (let i = 0; i < tratti.length; i++) {
    if (resto <= tratti[i] || i === tratti.length - 1) {
      const f = tratti[i] ? Math.min(resto / tratti[i], 1) : 0;
      return [punti[i][0] + (punti[i + 1][0] - punti[i][0]) * f, punti[i][1] + (punti[i + 1][1] - punti[i][1]) * f];
    }
    resto -= tratti[i];
  }
  return punti[0];
}

export function creaLivelloRaccordi(livello, geo, alCambioFile) {
  let firma = "";
  let disposti = new Map();
  let elementi = new Map();

  function aggiorna(raccordi, treni) {
    const nuovaFirma = raccordi.map((r) => r.id).join(";");
    if (nuovaFirma !== firma) {
      firma = nuovaFirma;
      const disposizione = disponi(raccordi, geo);
      disposti = disposizione.disposti;
      livello.replaceChildren();
      elementi = disegna(livello, disposti);
      alCambioFile(disposizione.file);
    }
    const occupati = new Set();
    const vicini = new Set(); // treni prossimi al bivio: il deviatoio è impegnato
    for (const t of treni) {
      const p = t.posizione;
      if (p?.stato !== "sul_raccordo") continue;
      occupati.add(p.raccordo_id);
      if (p.avanzamento < 0.35) vicini.add(p.raccordo_id);
    }
    for (const [id, { tronco, deviatoio }] of elementi) {
      tronco.classList.toggle("occupato", occupati.has(id));
      deviatoio.classList.toggle("itinerario", vicini.has(id));
    }
  }

  /** Coordinate di un treno sul raccordo, e verso del movimento sullo schermo. */
  function punto(idRaccordo, avanzamento, entrata) {
    const d = disposti.get(idRaccordo);
    if (!d) return null;
    const [x, y] = puntoLungo(d.punti, avanzamento);
    // In entrata ci si muove verso il bivio, cioè in senso opposto all'esterno.
    return { x, y, versoSchermo: entrata ? -d.verso : d.verso };
  }

  return { aggiorna, punto };
}
