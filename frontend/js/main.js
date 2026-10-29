// Avvio dello schermo: carica la linea, si collega in diretta e aggiorna tutto.

import { creaDettaglioTreno } from "./pannelli/dettaglio_treno.js";
import { creaElencoIncroci } from "./pannelli/elenco_incroci.js";
import { creaElencoTreni } from "./pannelli/elenco_treni.js";
import { mostraLegenda } from "./pannelli/legenda.js";
import { avviaOrologio, mostraConnessionePersa, mostraLinea, mostraStatoFonte } from "./pannelli/testata.js";
import { caricaLinea } from "./rete/api.js";
import { collegaDiretta } from "./rete/diretta.js";
import { creaQuadro } from "./sinottico/quadro.js";

const stato = { istantanea: null, selezionato: null };

async function avvia() {
  avviaOrologio();
  const linea = await caricaLinea();
  mostraLinea(linea);
  mostraLegenda(linea);

  const dettaglio = creaDettaglioTreno();
  const seleziona = (chiave) => {
    stato.selezionato = chiave;
    dettaglio.mostra(chiave);
    ridisegna();
  };

  const quadro = creaQuadro(document.getElementById("sinottico"), linea, seleziona);
  const elencoTreni = creaElencoTreni(linea, seleziona);
  const elencoIncroci = creaElencoIncroci(linea);

  function ridisegna() {
    const ist = stato.istantanea;
    if (!ist) return;
    mostraStatoFonte(ist.fonte);
    quadro.aggiorna(ist, stato.selezionato);
    elencoTreni.aggiorna(ist.treni, stato.selezionato);
    elencoIncroci.aggiorna(ist.incroci, ist.treni);
  }

  collegaDiretta({
    aggiornamento: (istantanea) => {
      stato.istantanea = istantanea;
      ridisegna();
    },
    connessionePersa: mostraConnessionePersa,
  });
}

avvia();
