// Mette insieme i livelli del quadro sinottico in un unico SVG.

import { svg } from "../util/dom.js";
import { ALTEZZA, LARGHEZZA_MINIMA, creaGeometria } from "./geometria.js";
import { creaLivelloIncroci } from "./incroci.js";
import { aggiornaOccupazioni } from "./occupazioni.js";
import { PASSO_FILE, Y_PRIMA_FILA, creaLivelloRaccordi } from "./raccordi.js";
import { disegnaRete } from "./rete.js";
import { creaLivelloTreni } from "./treni.js";

export function creaQuadro(elementoSvg, lineaDati, alClicTreno) {
  const geo = creaGeometria(lineaDati);
  elementoSvg.setAttribute("viewBox", `0 0 ${geo.larghezza} ${ALTEZZA}`);
  // Linee con molte stazioni: il quadro si allarga e la sezione scorre in orizzontale.
  if (geo.larghezza > LARGHEZZA_MINIMA) elementoSvg.style.minWidth = `${Math.round(geo.larghezza * 0.75)}px`;

  const livelloRete = svg("g");
  const livelloRaccordi = svg("g");
  const livelloIncroci = svg("g");
  const livelloTreni = svg("g");
  elementoSvg.replaceChildren(livelloRaccordi, livelloRete, livelloIncroci, livelloTreni);

  // Il quadro si allunga verso il basso quanto servono le file dei raccordi.
  const adattaAltezza = (file) => {
    const altezza = file ? Y_PRIMA_FILA + (file - 1) * PASSO_FILE + 20 : ALTEZZA;
    elementoSvg.setAttribute("viewBox", `0 0 ${geo.larghezza} ${Math.max(altezza, ALTEZZA)}`);
  };

  const elementiRete = disegnaRete(livelloRete, geo, lineaDati);
  const raccordi = creaLivelloRaccordi(livelloRaccordi, geo, adattaAltezza);
  const incroci = creaLivelloIncroci(livelloIncroci, geo);
  const treni = creaLivelloTreni(livelloTreni, geo, alClicTreno);

  function aggiorna(istantanea, selezionato) {
    const sigle = new Map(istantanea.treni.map((t) => [t.chiave, t.sigla]));
    aggiornaOccupazioni(elementiRete, geo, lineaDati, istantanea.treni);
    raccordi.aggiorna(istantanea.raccordi || [], istantanea.treni);
    incroci.aggiorna(istantanea.incroci, istantanea.ora, (chiave) => sigle.get(chiave) || "?");
    treni.aggiorna(istantanea.treni, selezionato, raccordi.punto);
  }

  return { aggiorna };
}
