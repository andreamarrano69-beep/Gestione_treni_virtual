// Pulsanti per mostrare o nascondere i treni di ogni categoria.
// La scelta resta salvata nel browser.

import { html } from "../util/dom.js";
import { gruppoCategoria } from "../util/formato.js";

const GRUPPI = [
  ["frecce", "Frecce / AV"],
  ["ic", "Intercity / EC"],
  ["reg", "Regionali"],
  ["altro", "Altri"],
];
const CHIAVE_MEMORIA = "filtro-categorie-nascoste";

function leggiNascosti() {
  try {
    return new Set(JSON.parse(localStorage.getItem(CHIAVE_MEMORIA)) || []);
  } catch {
    return new Set();
  }
}

function salvaNascosti(nascosti) {
  try {
    localStorage.setItem(CHIAVE_MEMORIA, JSON.stringify([...nascosti]));
  } catch {
    // senza memoria del browser il filtro vale solo fino al prossimo caricamento
  }
}

export function creaFiltroCategorie(alCambio) {
  const contenitore = document.getElementById("filtro-categorie");
  const nascosti = leggiNascosti();
  const pulsanti = new Map();

  contenitore.replaceChildren(html("span", { class: "filtro__etichetta", testo: "Mostra" }));
  for (const [gruppo, nome] of GRUPPI) {
    const colore = html("span", { class: "filtro__colore" });
    colore.style.background = `var(--cat-${gruppo})`;
    const numero = html("span", { class: "filtro__numero" });
    const pulsante = html("button", { type: "button", class: "filtro__voce" }, [colore, nome, numero]);
    pulsante.setAttribute("aria-pressed", String(!nascosti.has(gruppo)));
    pulsante.addEventListener("click", () => {
      nascosti.has(gruppo) ? nascosti.delete(gruppo) : nascosti.add(gruppo);
      pulsante.setAttribute("aria-pressed", String(!nascosti.has(gruppo)));
      salvaNascosti(nascosti);
      alCambio();
    });
    pulsanti.set(gruppo, numero);
    contenitore.append(pulsante);
  }

  /** Toglie dall'istantanea i treni nascosti e gli incroci che li riguardano. */
  function filtra(istantanea) {
    const conteggi = new Map(GRUPPI.map(([g]) => [g, 0]));
    for (const t of istantanea.treni) {
      const g = gruppoCategoria(t.categoria);
      conteggi.set(g, conteggi.get(g) + 1);
    }
    for (const [gruppo, numero] of pulsanti) numero.textContent = `(${conteggi.get(gruppo)})`;

    const treni = istantanea.treni.filter((t) => !nascosti.has(gruppoCategoria(t.categoria)));
    const visibili = new Set(treni.map((t) => t.chiave));
    const incroci = istantanea.incroci.filter((i) => visibili.has(i.treno_a) && visibili.has(i.treno_b));
    return { ...istantanea, treni, incroci };
  }

  return { filtra };
}
