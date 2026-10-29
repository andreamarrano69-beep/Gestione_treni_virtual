// Dove disegnare ogni cosa: da chilometrica e binario a coordinate sullo schermo.
//
// Le stazioni non sono messe in scala pura (quelle vicine a Milano finirebbero
// una sopra l'altra): la posizione è metà in scala e metà a passo costante.

export const LARGHEZZA_MINIMA = 1900;
export const SPAZIO_PER_STAZIONE = 140; // sotto questa distanza le stazioni si accavallano
export const ALTEZZA = 360;
export const MARGINE = 90;
const MARGINE_DESTRO = 160; // spazio per il nome inclinato dell'ultima stazione
export const Y_CRESCENTE = 170; // binario di corsa per i treni verso km crescenti
export const Y_DECRESCENTE = 230; // binario di corsa per i treni verso km decrescenti
export const SEMI_STAZIONE = 18; // metà lunghezza dei binari di stazione
export const ZONA_DEVIATOI = 14; // spazio per i deviatoi ai lati della stazione

export function creaGeometria(linea) {
  const stazioni = linea.stazioni;
  const n = stazioni.length;
  const km0 = stazioni[0].km;
  const kmTot = stazioni[n - 1].km - km0 || 1;
  const larghezza = Math.max(LARGHEZZA_MINIMA, n * SPAZIO_PER_STAZIONE);
  const utile = larghezza - MARGINE - MARGINE_DESTRO;

  const xs = stazioni.map(
    (s, i) => MARGINE + utile * (0.5 * (n > 1 ? i / (n - 1) : 0) + (0.5 * (s.km - km0)) / kmTot),
  );
  const indice = new Map(stazioni.map((s, i) => [s.id, i]));

  function xDaKm(km) {
    if (km <= stazioni[0].km) return xs[0];
    for (let i = 1; i < n; i++) {
      if (km <= stazioni[i].km) {
        const f = (km - stazioni[i - 1].km) / (stazioni[i].km - stazioni[i - 1].km || 1);
        return xs[i - 1] + (xs[i] - xs[i - 1]) * f;
      }
    }
    return xs[n - 1];
  }

  /** Quote verticali dei binari di stazione, dall'alto in basso. */
  function yBinari(stazione) {
    const k = stazione.binari.length;
    if (k <= 2) return k === 1 ? [Y_CRESCENTE] : [Y_CRESCENTE, Y_DECRESCENTE];
    const sporgenza = Math.min(30, (k - 2) * 8);
    const alto = Y_CRESCENTE - sporgenza;
    const passo = (Y_DECRESCENTE + sporgenza - alto) / (k - 1);
    return stazione.binari.map((_, j) => alto + j * passo);
  }

  /** Indice del binario su cui disegnare un treno in stazione. */
  function indiceBinario(stazione, binario, direzione) {
    const j = stazione.binari.indexOf(binario);
    if (j >= 0) return j;
    const yCorsa = direzione > 0 ? Y_CRESCENTE : Y_DECRESCENTE;
    const ys = yBinari(stazione);
    return ys.reduce((migliore, y, i) => (Math.abs(y - yCorsa) < Math.abs(ys[migliore] - yCorsa) ? i : migliore), 0);
  }

  return {
    larghezza,
    xDaKm,
    xStazione: (id) => xs[indice.get(id)],
    stazione: (id) => stazioni[indice.get(id)],
    yBinari,
    indiceBinario,
    yCorsa: (direzione) => (direzione > 0 ? Y_CRESCENTE : Y_DECRESCENTE),
  };
}
