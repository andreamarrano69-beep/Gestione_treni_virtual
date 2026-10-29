// Piccoli aiuti per creare elementi HTML e SVG.

const SVG_NS = "http://www.w3.org/2000/svg";

export function svg(tag, attributi = {}, figli = []) {
  const nodo = document.createElementNS(SVG_NS, tag);
  for (const [nome, valore] of Object.entries(attributi)) nodo.setAttribute(nome, valore);
  for (const figlio of figli) nodo.append(figlio);
  return nodo;
}

export function html(tag, attributi = {}, figli = []) {
  const nodo = document.createElement(tag);
  for (const [nome, valore] of Object.entries(attributi)) {
    if (nome === "testo") nodo.textContent = valore;
    else nodo.setAttribute(nome, valore);
  }
  for (const figlio of figli) nodo.append(figlio);
  return nodo;
}
