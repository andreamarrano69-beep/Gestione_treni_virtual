// Legenda dei colori sotto il quadro.

import { html } from "../util/dom.js";

const VOCI = [
  ["var(--cat-frecce)", "Frecce / AV"],
  ["var(--cat-ic)", "Intercity / EC"],
  ["var(--cat-reg)", "Regionali"],
  ["var(--cat-altro)", "Altri"],
  ["var(--occupato)", "Binario occupato"],
  ["var(--itinerario)", "Itinerario (dedotto dal binario)"],
  ["var(--incrocio)", "Incrocio previsto"],
  ["var(--precedenza)", "Precedenza prevista"],
];

export function mostraLegenda(lineaDati) {
  const elenco = document.getElementById("legenda");
  elenco.replaceChildren(
    ...VOCI.map(([colore, testo]) => {
      const campione = html("span", { class: "legenda__campione" });
      campione.style.background = colore;
      return html("li", {}, [campione, testo]);
    }),
    html("li", { testo: `Binario alto: ${lineaDati.verso_crescente} · basso: ${lineaDati.verso_decrescente}` }),
  );
}
