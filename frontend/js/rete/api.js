// Richieste HTTP al backend.

async function leggi(percorso) {
  const risposta = await fetch(percorso);
  if (!risposta.ok) throw new Error(`${percorso}: ${risposta.status}`);
  return risposta.json();
}

export const caricaLinea = () => leggi("api/linea");
export const caricaDettaglioTreno = (chiave) => leggi(`api/treni/${encodeURIComponent(chiave)}`);
