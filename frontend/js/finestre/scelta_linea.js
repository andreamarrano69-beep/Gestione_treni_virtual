// Finestra pop-up per cambiare linea:
//   - riaprire una linea già salvata, oppure
//   - scegliere la stazione di partenza, poi una destinazione servita da lì:
//     il server ricostruisce la linea dalle fermate dei treni e la attiva.

import { attivaLinea, cercaStazioni, creaLinea, destinazioniDa, elencoLinee } from "../rete/api.js";
import { html } from "../util/dom.js";
import { nomeProprio } from "../util/formato.js";
import { mostraMessaggio, mostraScelte } from "./elenco_scelte.js";

const ATTESA_DIGITAZIONE_MS = 300;

function passo(titolo, ...contenuto) {
  return html("section", { class: "finestra__passo" }, [html("h3", { testo: titolo }), ...contenuto]);
}

function costruisci(finestra) {
  const chiudi = html("button", { type: "button", class: "finestra__chiudi", "aria-label": "Chiudi", testo: "×" });
  chiudi.addEventListener("click", () => finestra.close());
  const parti = {
    salvate: html("ul", { class: "scelte" }),
    ricerca: html("input", { type: "search", placeholder: "Scrivi il nome della stazione, es. Lodi", autocomplete: "off" }),
    stazioni: html("ul", { class: "scelte" }),
    destinazioni: html("ul", { class: "scelte" }),
    passoDestinazioni: null,
    messaggio: html("p", { class: "messaggio" }),
  };
  parti.passoDestinazioni = passo("2 · Destinazione", parti.destinazioni);
  parti.passoDestinazioni.hidden = true;

  finestra.replaceChildren(
    html("header", { class: "finestra__testata" }, [
      html("h2", { id: "titolo-finestra-linea", testo: "Scegli la linea" }),
      chiudi,
    ]),
    html("div", { class: "finestra__corpo" }, [
      passo("Linee salvate", parti.salvate),
      passo("1 · Stazione di partenza per una nuova linea", parti.ricerca, parti.stazioni),
      parti.passoDestinazioni,
      parti.messaggio,
    ]),
  );
  return parti;
}

export function creaSceltaLinea() {
  const finestra = document.getElementById("finestra-linea");
  const parti = costruisci(finestra);
  let timer = null;

  async function esegui(testoAttesa, azione) {
    mostraMessaggio(parti.messaggio, testoAttesa);
    try {
      await azione();
    } catch (errore) {
      mostraMessaggio(parti.messaggio, errore.message, true);
    }
  }

  const ricaricaSchermo = () => location.reload();

  async function mostraSalvate() {
    const { attiva, linee } = await elencoLinee();
    mostraScelte(
      parti.salvate,
      linee.map((l) => ({
        testo: l.nome,
        dettagli: l.id === attiva ? "● attiva" : "",
        classeDettagli: "attiva",
        valore: l.id,
      })),
      (id) => esegui("Attivo la linea…", async () => {
        await attivaLinea(id);
        ricaricaSchermo();
      }),
    );
  }

  function scegliStazione(stazione) {
    parti.passoDestinazioni.hidden = false;
    parti.destinazioni.replaceChildren();
    esegui(`Leggo il tabellone di ${nomeProprio(stazione.nome)}…`, async () => {
      const destinazioni = await destinazioniDa(stazione);
      mostraMessaggio(parti.messaggio, destinazioni.length ? "" : "Nessun treno in partenza o in arrivo adesso.");
      mostraScelte(
        parti.destinazioni,
        destinazioni.map((d) => ({
          testo: nomeProprio(d.capolinea),
          dettagli: `${d.treni} treni · ${d.categorie.join(" ")}`,
          valore: d.capolinea,
        })),
        (capolinea) => esegui("Costruisco la linea dalle fermate dei treni… (qualche secondo)", async () => {
          await creaLinea(stazione, capolinea);
          ricaricaSchermo();
        }),
      );
    });
  }

  parti.ricerca.addEventListener("input", () => {
    clearTimeout(timer);
    const testo = parti.ricerca.value.trim();
    timer = setTimeout(() => esegui("", async () => {
      const stazioni = testo.length >= 2 ? await cercaStazioni(testo) : [];
      mostraScelte(
        parti.stazioni,
        stazioni.map((s) => ({ testo: nomeProprio(s.nome), dettagli: s.codice, valore: s })),
        scegliStazione,
      );
    }), ATTESA_DIGITAZIONE_MS);
  });

  function apri() {
    finestra.showModal();
    parti.ricerca.focus();
    esegui("", mostraSalvate);
  }

  return { apri };
}
