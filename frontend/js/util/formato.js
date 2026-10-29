// Formattazione di orari, ritardi, categorie e nomi.

const FORMATO_ORA = new Intl.DateTimeFormat("it-IT", {
  hour: "2-digit", minute: "2-digit", timeZone: "Europe/Rome",
});
const FORMATO_ORA_SECONDI = new Intl.DateTimeFormat("it-IT", {
  hour: "2-digit", minute: "2-digit", second: "2-digit", timeZone: "Europe/Rome",
});

export const ora = (ms) => (ms ? FORMATO_ORA.format(ms) : "--:--");
export const oraConSecondi = (ms) => FORMATO_ORA_SECONDI.format(ms);

const FRECCE = ["FR", "FA", "FB", "ES", "ESC", "AV"];
const INTERCITY = ["IC", "ICN", "EC", "EN"];
const REGIONALI = ["REG", "RV", "R", "S", "MET", "RE"];

export function gruppoCategoria(categoria) {
  const c = (categoria || "").toUpperCase();
  if (FRECCE.includes(c)) return "frecce";
  if (INTERCITY.includes(c)) return "ic";
  if (REGIONALI.includes(c)) return "reg";
  return "altro";
}

export const coloreCategoria = (categoria) => `var(--cat-${gruppoCategoria(categoria)})`;

export function coloreRitardo(minuti) {
  if (minuti <= 0) return "var(--ritardo-ok)";
  if (minuti <= 5) return "var(--ritardo-lieve)";
  if (minuti <= 15) return "var(--ritardo-medio)";
  return "var(--ritardo-grave)";
}

export const testoRitardo = (minuti) => (minuti > 0 ? `+${minuti}'` : minuti < 0 ? `${minuti}'` : "in orario");

/** "MILANO CENTRALE" -> "Milano Centrale" */
export function nomeProprio(testo) {
  return (testo || "").toLowerCase().replace(/(^|[\s'.-])\S/g, (s) => s.toUpperCase());
}
