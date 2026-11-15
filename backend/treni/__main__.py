"""Avvio: `python -m treni` dalla cartella backend.

Con `python -m treni --rete` il quadro si apre anche dagli altri dispositivi
della rete di casa (telefono, tablet, TV) all'indirizzo che viene stampato.
"""

import argparse
import logging
import socket
from dataclasses import replace

import uvicorn

from treni.app import crea_app
from treni.config import carica_impostazioni


def indirizzo_in_rete_locale() -> str:
    """L'indirizzo di questo PC nella rete di casa (es. 192.168.1.20)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("10.255.255.255", 1))  # nessun pacchetto viene davvero inviato
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def main() -> None:
    argomenti = argparse.ArgumentParser(description="Quadro sinottico dei treni")
    argomenti.add_argument("--rete", action="store_true", help="raggiungibile da telefono e altri dispositivi di casa")
    rete = argomenti.parse_args().rete

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    imp = carica_impostazioni()
    if rete:
        imp = replace(imp, host="0.0.0.0")
    print(f"Quadro sinottico su http://127.0.0.1:{imp.porta}  (fonte: {imp.fonte}, linea: {imp.linea})")
    if imp.host == "0.0.0.0":
        print(f"Dal telefono (stessa Wi-Fi): http://{indirizzo_in_rete_locale()}:{imp.porta}")
    # Senza un limite, alla chiusura il server aspetterebbe per sempre che il
    # browser chiuda il collegamento in diretta, e Ctrl+C sembrerebbe non funzionare.
    uvicorn.run(crea_app(imp), host=imp.host, port=imp.porta, timeout_graceful_shutdown=2)


if __name__ == "__main__":
    main()
