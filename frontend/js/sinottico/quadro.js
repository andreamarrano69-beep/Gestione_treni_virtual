// Mette insieme i livelli del quadro sinottico in un unico SVG.

import { svg } from "../util/dom.js";
import { ALTEZZA, LARGHEZZA_MINIMA, creaGeometria } from "./geometria.js";
import { creaLivelloIncroci } from "./incroci.js";
import { aggiornaOccupazioni } from "./occupazioni.js";
import { disegnaRete } from "./rete.js";
import { creaLivelloTreni } from "./treni.js";

export function creaQuadro(elementoSvg, lineaDati, alClicTreno) {
  const geo = creaGeometria(lineaDati);
  elementoSvg.setAttribute("viewBox", `0 0 ${geo.larghezza} ${ALTEZZA}`);
  // Linee con molte stazioni: il quadro si allarga e la sezione scorre in orizzontale.
  if (geo.larghezza > LARGHEZZA_MINIMA) elementoSvg.style.minWidth = `${Math.round(geo.larghezza * 0.75)}px`;

  const livelloRete = svg("g");
  const livelloIncroci = svg("g");
  const livelloTreni = svg("g");
  elementoSvg.replaceChildren(livelloRete, livelloIncroci, livelloTreni);

  const elementiRete = disegnaRete(livelloRete, geo, lineaDati);
  const incroci = creaLivelloIncroci(livelloIncroci, geo);
  const treni = creaLivelloTreni(livelloTreni, geo, alClicTreno);

  function aggiorna(istantanea, selezionato) {
    const sigle = new Map(istantanea.treni.map((t) => [t.chiave, t.sigla]));
    aggiornaOccupazioni(elementiRete, geo, lineaDati, istantanea.treni);
    incroci.aggiorna(istantanea.incroci, istantanea.ora, (chiave) => sigle.get(chiave) || "?");
    treni.aggiorna(istantanea.treni, selezionato);
  }

  return { aggiorna };
}
