// Elenco di voci cliccabili usato nei passi della finestra "Scegli linea".

import { html } from "../util/dom.js";

/** voci: [{ testo, dettagli, classeDettagli, valore }] */
export function mostraScelte(lista, voci, alClic) {
  lista.replaceChildren(
    ...voci.map((voce) => {
      const pulsante = html("button", { type: "button" }, [
        html("span", { testo: voce.testo }),
        html("span", { class: `dettagli ${voce.classeDettagli || ""}`, testo: voce.dettagli || "" }),
      ]);
      pulsante.addEventListener("click", () => {
        for (const altro of lista.querySelectorAll("button")) altro.classList.remove("scelta");
        pulsante.classList.add("scelta");
        alClic(voce.valore);
      });
      return html("li", {}, [pulsante]);
    }),
  );
}

export function mostraMessaggio(elemento, testo, errore = false) {
  elemento.textContent = testo;
  elemento.className = errore ? "messaggio messaggio--errore" : "messaggio";
}
