// Service worker: rende il quadro installabile come app sul telefono.
// I dati dei treni arrivano sempre dal server; si tiene in memoria solo la
// grafica, per aprire subito l'app e mostrare un avviso se il PC è spento.

const CACHE = "quadro-sinottico-v1";

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (evento) => evento.waitUntil(self.clients.claim()));

self.addEventListener("fetch", (evento) => {
  const indirizzo = new URL(evento.request.url);
  if (evento.request.method !== "GET" || indirizzo.pathname.includes("/api/")) return;
  // Prima la rete (versione sempre aggiornata), la copia salvata solo se il server non risponde.
  evento.respondWith(
    fetch(evento.request)
      .then((risposta) => {
        const copia = risposta.clone();
        caches.open(CACHE).then((cache) => cache.put(evento.request, copia));
        return risposta;
      })
      .catch(() => caches.match(evento.request)),
  );
});
