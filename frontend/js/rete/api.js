// Richieste HTTP al backend.

async function leggi(percorso, opzioni) {
  const risposta = await fetch(percorso, opzioni);
  if (!risposta.ok) {
    const errore = await risposta.json().catch(() => ({}));
    throw new Error(errore.detail || `${percorso}: ${risposta.status}`);
  }
  return risposta.json();
}

function invia(percorso, dati) {
  return leggi(percorso, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dati),
  });
}

export const caricaLinea = () => leggi("api/linea");
export const caricaDettaglioTreno = (chiave) => leggi(`api/treni/${encodeURIComponent(chiave)}`);

export const elencoLinee = () => leggi("api/linee");
export const attivaLinea = (id) => invia("api/linee/attiva", { id });
export const cercaStazioni = (testo) => leggi(`api/stazioni?testo=${encodeURIComponent(testo)}`);
export const destinazioniDa = (stazione) =>
  leggi(`api/stazioni/${encodeURIComponent(stazione.codice)}/destinazioni?nome=${encodeURIComponent(stazione.nome)}`);
export const creaLinea = (stazione, capolinea) =>
  invia("api/linee/crea", { codice: stazione.codice, nome: stazione.nome, capolinea });
