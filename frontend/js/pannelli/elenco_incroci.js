// Elenco dei prossimi incroci (direzioni opposte) e precedenze (sorpassi).

import { html } from "../util/dom.js";
import { ora } from "../util/formato.js";

const MASSIMO = 20;

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
        const incrocio = i.tipo === "incrocio";
        return html("li", { title: incrocio ? "Incrocio" : "Precedenza (sorpasso)" }, [
          html("span", { testo: ora(i.ora) }),
          html("span", { class: incrocio ? "icona-incrocio" : "icona-precedenza", testo: incrocio ? "⇄" : "⇉" }),
          html("span", { testo: `${sigle.get(i.treno_a) || "?"}  ·  ${sigle.get(i.treno_b) || "?"}` }),
          html("span", { class: "luogo", testo: `presso ${nomi.get(i.stazione_vicina_id)} (km ${i.km.toFixed(1)})` }),
        ]);
      }),
    );
  }
  return { aggiorna };
}
