"""Avvio: `python -m treni` dalla cartella backend."""

import logging

import uvicorn

from treni.app import crea_app
from treni.config import carica_impostazioni


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    imp = carica_impostazioni()
    print(f"Quadro sinottico su http://{imp.host}:{imp.porta}  (fonte: {imp.fonte}, linea: {imp.linea})")
    # Senza un limite, alla chiusura il server aspetterebbe per sempre che il
    # browser chiuda il collegamento in diretta, e Ctrl+C sembrerebbe non funzionare.
    uvicorn.run(crea_app(imp), host=imp.host, port=imp.porta, timeout_graceful_shutdown=2)


if __name__ == "__main__":
    main()
