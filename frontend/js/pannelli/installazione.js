// Installazione come app (PWA) su telefono o PC.
//
// Chrome permette l'installazione solo da indirizzi sicuri (https o localhost).
// Il pulsante "Installa app" compare quando Chrome è pronto; se l'indirizzo non
// è considerato sicuro, un avviso dice esattamente cosa scrivere nel flag di Chrome.

const FLAG = "chrome://flags/#unsafely-treat-insecure-origin-as-secure";

export function preparaInstallazione() {
  const pulsante = document.getElementById("installa-app");
  const avviso = document.getElementById("avviso-installazione");
  const giaInstallata = window.matchMedia("(display-mode: standalone)").matches;
  if (giaInstallata) return;

  if (!window.isSecureContext) {
    avviso.hidden = false;
    avviso.textContent =
      `Per installare l'app su Android: apri ${FLAG}, scrivi ${location.origin} ` +
      `(esattamente così), metti Enabled, premi Riavvia e ricarica questa pagina.`;
    return;
  }

  navigator.serviceWorker?.register("sw.js").catch(() => {});

  let richiesta = null;
  window.addEventListener("beforeinstallprompt", (evento) => {
    evento.preventDefault(); // la mostriamo noi quando si preme il pulsante
    richiesta = evento;
    pulsante.hidden = false;
  });
  pulsante.addEventListener("click", async () => {
    if (!richiesta) return;
    richiesta.prompt();
    await richiesta.userChoice;
    richiesta = null;
    pulsante.hidden = true;
  });
  window.addEventListener("appinstalled", () => (pulsante.hidden = true));
}
