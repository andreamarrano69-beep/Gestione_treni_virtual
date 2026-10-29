// Accende in rosso i binari occupati e in giallo i deviatoi dell'itinerario.

export function aggiornaOccupazioni(elementi, geo, lineaDati, treni) {
  const tratti = new Set();
  const binari = new Map(); // chiave binario -> direzione del treno

  for (const treno of treni) {
    const p = treno.posizione;
    if (!p) continue;
    if (p.stato === "in_linea") {
      tratti.add(chiaveTratto(lineaDati, p));
    } else {
      const stazione = geo.stazione(p.stazione_id);
      binari.set(`${p.stazione_id}|${geo.indiceBinario(stazione, p.binario, p.direzione)}`, p.direzione);
    }
  }

  for (const [chiave, tratto] of elementi.tratti) {
    tratto.classList.toggle("occupato", tratti.has(chiave));
  }
  for (const [chiave, { binario, deviatoi }] of elementi.binari) {
    const occupato = binari.has(chiave);
    binario.classList.toggle("occupato", occupato);
    // deviatoi[0] lato km minori, deviatoi[1] lato km maggiori: si accendono entrambi
    // perché il treno ci è entrato da un lato e ne uscirà dall'altro.
    for (const d of deviatoi) d.classList.toggle("itinerario", occupato);
  }
}

/** Il tratto è identificato dalla stazione di inizio (km minori) e dalla direzione. */
function chiaveTratto(lineaDati, p) {
  const ids = [p.da_stazione_id, p.a_stazione_id];
  const indici = ids.map((id) => lineaDati.stazioni.findIndex((s) => s.id === id));
  // Se il treno salta fermate il tratto è più lungo: si accende quello in cui si trova.
  const tratti = lineaDati.stazioni.slice(Math.min(...indici), Math.max(...indici));
  const attuale = tratti.filter((s) => s.km <= p.km).pop() || tratti[0];
  return `${attuale.id}|${p.direzione}`;
}
