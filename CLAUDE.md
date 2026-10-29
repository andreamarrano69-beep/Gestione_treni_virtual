# Regole del progetto

- **File corti**: ogni file sotto le ~150 righe e con un solo compito. Se un file
  cresce, dividilo in moduli nella cartella giusta invece di allungarlo.
- Nomi di variabili, funzioni, commenti e messaggi in **italiano**.
- Il backend non conosce il frontend e viceversa: comunicano solo tramite il
  JSON prodotto in `backend/treni/api/serializzazione.py`.
- Ogni nuova fonte dati implementa il contratto `FonteDati` in
  `backend/treni/fonti/base.py`; la logica in `servizi/` non deve dipendere da
  una fonte specifica.
- Frontend senza passaggi di compilazione: moduli ES nativi, nessuna libreria esterna.
- Le linee si descrivono in `dati/linee/*.yaml`, mai nel codice.

## Comandi

```bash
cd backend && python -m pytest                 # test
cd backend && TRENI_FONTE=demo python -m treni # avvio con treni simulati
```
