// Collegamento WebSocket al backend, con riconnessione automatica.

const ATTESA_RICONNESSIONE_MS = 3000;

export function collegaDiretta({ aggiornamento, connessionePersa }) {
  const protocollo = location.protocol === "https:" ? "wss" : "ws";
  const indirizzo = `${protocollo}://${location.host}${location.pathname.replace(/[^/]*$/, "")}ws`;

  function apri() {
    const socket = new WebSocket(indirizzo);
    socket.onmessage = (evento) => aggiornamento(JSON.parse(evento.data));
    socket.onclose = () => {
      connessionePersa();
      setTimeout(apri, ATTESA_RICONNESSIONE_MS);
    };
  }
  apri();
}
