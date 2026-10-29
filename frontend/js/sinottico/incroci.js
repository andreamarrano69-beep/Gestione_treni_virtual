// Segna sul quadro dove avverranno i prossimi incroci e precedenze.
// L'orario compare passandoci sopra col mouse e nel pannello degli incroci.

import { svg } from "../util/dom.js";
import { ora } from "../util/formato.js";
import { Y_CRESCENTE, Y_DECRESCENTE } from "./geometria.js";

const Y = (Y_CRESCENTE + Y_DECRESCENTE) / 2;
const ENTRO_MS = 15 * 60 * 1000; // sul quadro solo quelli dei prossimi 15 minuti

export function creaLivelloIncroci(livello, geo) {
  function aggiorna(incroci, adessoMs, siglaDi) {
    livello.replaceChildren();
    for (const incrocio of incroci) {
      if (incrocio.ora - adessoMs > ENTRO_MS) continue;
      const x = geo.xDaKm(incrocio.km);
      const gruppo = svg("g", { class: `incrocio incrocio--${incrocio.tipo}`, transform: `translate(${x} ${Y})` });
      gruppo.append(svg("polygon", { class: "incrocio__segno", points: "0,-6 6,0 0,6 -6,0" }));
      gruppo.append(svg("title", {}, [
        `${incrocio.tipo === "incrocio" ? "Incrocio" : "Precedenza"} ${siglaDi(incrocio.treno_a)} / ${siglaDi(incrocio.treno_b)} alle ${ora(incrocio.ora)}`,
      ]));
      livello.append(gruppo);
    }
  }
  return { aggiorna };
}
