// Elenco dei prossimi incroci (direzioni opposte), precedenze (sorpassi)
// e conflitti al bivio (un treno entra o esce mentre un altro passa).

import { html } from "../util/dom.js";
import { ora } from "../util/formato.js";

const MASSIMO = 20;
const TIPI = {
  incrocio: { icona: "⇄", classe: "icona-incrocio", titolo: "Incrocio" },
  precedenza: { icona: "⇉", classe: "icona-precedenza", titolo: "Precedenza (sorpasso)" },
  bivio: { icona: "⋔", classe: "icona-bivio", titolo: "Conflitto al bivio: uno dei due deve attendere" },
};

export function creaElencoIncroci(lineaDati) {
  const lista = document.getElementById("lista-incroci");
  const nomi = new Map(lineaDati.stazioni.map((s) => [s.id, s.nome]));

  function aggiorna(incroci, treni) {
    const sigle = new Map(treni.map((t) => [t.chiave, t.sigla]));
    if (!incroci.length) {
      lista.replaceChildren(html("li", { class: "vuoto", testo: "Nessun incrocio previsto." }));
      return;
    }
    lista.replaceChildren(
      ...incroci.slice(0, MASSIMO).map((i) => {
        const tipo = TIPI[i.tipo] || TIPI.incrocio;
        const luogo = i.tipo === "bivio"
          ? `bivio di ${nomi.get(i.stazione_vicina_id)}`
          : `presso ${nomi.get(i.stazione_vicina_id)} (km ${i.km.toFixed(1)})`;
        return html("li", { title: tipo.titolo }, [
          html("span", { testo: ora(i.ora) }),
          html("span", { class: tipo.classe, testo: tipo.icona }),
          html("span", { testo: `${sigle.get(i.treno_a) || "?"}  ·  ${sigle.get(i.treno_b) || "?"}` }),
          html("span", { class: "luogo", testo: luogo }),
        ]);
      }),
    );
  }
  return { aggiorna };
}
