# Gestione Treni Virtual

Un **quadro sinottico** in stile sala circolazione RFI che mostra i treni reali
italiani in diretta su una linea ferroviaria: posizione dei treni, binari
occupati, stazioni, deviatoi, ritardi, incroci e precedenze previsti.

I dati arrivano da **ViaggiaTreno** (RFI/Trenitalia). Per provare senza
internet c'è anche una **sorgente demo** con treni simulati.

## Cosa mostra e cosa no

| Mostrato | Da dove arriva |
|---|---|
| Treni sulla linea, numero, categoria, ritardo | ViaggiaTreno, dato reale |
| Binario di stazione occupato | ViaggiaTreno, binario effettivo o programmato |
| Posizione del treno tra due stazioni | **Stimata**: interpolata tra i passaggi rilevati, non è GPS |
| Incroci e precedenze futuri | **Previsti** dagli orari stimati |
| Deviatoi in giallo (itinerario) | **Dedotti** dal binario di stazione occupato |

Lo stato reale di deviatoi e segnali non è pubblico, quindi non può essere mostrato.

## Avvio

Serve Python 3.11 o più recente.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # su Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m treni
```

Poi apri **http://127.0.0.1:8000** nel browser (meglio a tutto schermo, tasto F11).

Per i treni simulati:

```bash
TRENI_FONTE=demo python -m treni          # su Windows: set TRENI_FONTE=demo && python -m treni
```

### Impostazioni (variabili d'ambiente)

| Variabile | Predefinito | Significato |
|---|---|---|
| `TRENI_FONTE` | `viaggiatreno` | `viaggiatreno` (dati reali) oppure `demo` |
| `TRENI_LINEA` | `milano_bologna` | file della linea in `dati/linee/` |
| `TRENI_PORTA` | `8000` | porta del server |
| `TRENI_HOST` | `127.0.0.1` | `0.0.0.0` per aprirlo da altri dispositivi (es. una TV) |
| `TRENI_INTERVALLO_ANDAMENTO` | `60` | secondi tra un aggiornamento dei treni e l'altro |
| `TRENI_INTERVALLO_SCOPERTA` | `300` | secondi tra una ricerca di nuovi treni e l'altra |
| `TRENI_ORIZZONTE_INCROCI` | `30` | minuti di previsione degli incroci |

## Filtro per categoria

Sopra il quadro i pulsanti **Frecce / AV**, **Intercity / EC**, **Regionali** e
**Altri** mostrano o nascondono i treni di quella categoria (con il loro numero).
Gli incroci con un treno nascosto spariscono anche dall'elenco. La scelta resta
memorizzata nel browser.

## Cambiare linea

Il pulsante **Scegli linea…** apre una finestra dove puoi:

1. riaprire una delle **linee salvate**, oppure
2. cercare una **stazione di partenza**, vedere tutte le **destinazioni** servite
   in questo momento (con numero di treni e categorie) e sceglierne una.

Il programma prende i treni verso quella destinazione, preferendo i regionali
che fermano ovunque, e usa le loro fermate reali come stazioni della linea. I km
sono approssimati: in linea d'aria tra le stazioni, oppure stimati dai tempi di
percorrenza. La linea viene salvata in `dati/linee/` e attivata subito.

## Aggiungere una linea a mano

Copia `dati/linee/milano_bologna.yaml`, cambia stazioni, chilometriche e binari,
poi avvia con `TRENI_LINEA=<nome file>` o sceglila dalla finestra. I codici
ViaggiaTreno delle stazioni vengono cercati in automatico e salvati in `dati/cache/`.

## Test

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest
```

## Struttura

```
backend/treni/
  config.py              impostazioni
  app.py                 costruzione dell'applicazione web
  dominio/               oggetti base: Linea, Stazione, Treno, Fermata, Posizione, Incrocio
  linee/                 lettura dei file YAML delle linee e abbinamento fermate-stazioni
  fonti/                 da dove arrivano i dati
    base.py              contratto comune a tutte le fonti
    viaggiatreno/        client HTTP, parser JSON, codici stazioni
    demo/                orario simulato
  servizi/               la logica
    orario_stimato.py    orari reali o previsti di ogni fermata
    posizione.py         dove si trova un treno in un istante
    incroci.py           previsione di incroci e precedenze
    aggiornatore.py      cicli che interrogano la fonte
    gestore.py           linea attiva e cambio di linea
    tratte.py            destinazioni servite da una stazione
    costruttore_linea.py nuova linea dalle fermate dei treni
    distanze.py          km approssimati tra le fermate
    istantanea.py        fotografia della circolazione
  api/                   HTTP (/api/...) e WebSocket (/ws)
backend/tests/           test automatici
frontend/
  index.html
  css/                   stili separati per area dello schermo
  js/sinottico/          disegno del quadro (geometria, rete, treni, incroci, occupazioni)
  js/pannelli/           pannelli (testata, elenchi, dettaglio, legenda, filtro categorie)
  js/finestre/           finestra pop-up "Scegli linea"
  js/rete/               comunicazione col server
  js/util/               funzioni di supporto
dati/linee/              descrizioni delle linee
```

## Avvertenza

Le API di ViaggiaTreno non sono ufficiali e possono cambiare senza preavviso.
Il progetto è per uso personale e hobbistico.
