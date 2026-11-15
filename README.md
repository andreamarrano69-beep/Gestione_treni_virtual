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
| `TRENI_HOST` | `127.0.0.1` | `0.0.0.0` per aprirlo da altri dispositivi (come `--rete`) |
| `TRENI_INTERVALLO_ANDAMENTO` | `60` | secondi tra un aggiornamento dei treni e l'altro |
| `TRENI_INTERVALLO_SCOPERTA` | `300` | secondi tra una ricerca di nuovi treni e l'altra |
| `TRENI_ORIZZONTE_INCROCI` | `30` | minuti di previsione degli incroci |

## Raccordi: treni che entrano ed escono dalla linea

Ogni treno che ferma in almeno una stazione della linea viene seguito, anche se
arriva da un'altra linea o dall'estero (EC, EN, Railjet…) oppure ci va.
Sotto le stazioni dove questo succede compare un **raccordo**: un ramo
tratteggiato con il nome della prima fermata fuori linea (es. "◂ Monza").

- I treni **in arrivo** compaiono sul ramo fino a 10 minuti prima di lasciare la
  fermata precedente e avanzano verso il bivio, con i minuti mancanti ("tra 4'").
- I treni **in uscita** percorrono il ramo verso l'esterno e poi spariscono.
- Il tronco occupato diventa rosso; il deviatoio del bivio diventa giallo quando
  un treno è vicino.
- **Conflitto al bivio** (rombo bianco, simbolo ⋔ nell'elenco): un treno entra o
  esce mentre un altro passa dalla stessa stazione entro 3 minuti. Nella realtà
  uno dei due deve dare la precedenza.

Il bivio viene posto nella prima (o ultima) stazione della linea in cui il treno
ferma: se entra tra due stazioni senza fermarsi, il ramo è disegnato su quella
più vicina. Lo stato reale dei deviatoi non è pubblico: è dedotto dai treni.

## Sul telefono (Android) come app

Il PC fa da server: deve restare acceso con il programma avviato.

1. Avvia con `python -m treni --rete`: viene stampato l'indirizzo per il
   telefono, es. `http://192.168.1.20:8000`. La prima volta Windows chiede il
   permesso del firewall: consenti l'accesso sulle **reti private**.
2. Sul telefono, collegato alla **stessa Wi-Fi**, apri quell'indirizzo in Chrome.
3. Menu ⋮ → **Aggiungi a schermata Home**.

Chrome installa una vera app (a tutto schermo, con icona) solo da indirizzi
sicuri. Per averla da `http://192.168…`: sul telefono apri
`chrome://flags/#unsafely-treat-insecure-origin-as-secure`, scrivi l'indirizzo
del PC (es. `http://192.168.1.20:8000`), imposta **Enabled**, riavvia Chrome e
poi menu ⋮ → **Installa app**. Senza questo passaggio l'icona sulla Home apre
comunque il quadro, ma dentro una scheda di Chrome.

## Filtro per categoria

Sopra il quadro i pulsanti **Frecce / AV**, **Intercity**, **Internazionali**
(EC, EN, Railjet, TGV…), **Regionali** e **Altri** mostrano o nascondono i treni di quella categoria (con il loro numero).
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
    lati.py              da che lato della stazione si entra o si esce
    raccordi.py          treni in arrivo da altre linee o in uscita
    conflitti_bivio.py   treni che impegnano lo stesso bivio
    istantanea.py        fotografia della circolazione
  api/                   HTTP (/api/...) e WebSocket (/ws)
backend/tests/           test automatici
frontend/
  index.html
  css/                   stili separati per area dello schermo
  js/sinottico/          disegno del quadro (geometria, rete, raccordi, treni, incroci, occupazioni)
  js/pannelli/           pannelli (testata, elenchi, dettaglio, legenda, filtro categorie)
  js/finestre/           finestra pop-up "Scegli linea"
  js/rete/               comunicazione col server
  js/util/               funzioni di supporto
  manifest.json, sw.js   installazione come app (PWA)
  icone/                 icone dell'app
dati/linee/              descrizioni delle linee
```

## Avvertenza

Le API di ViaggiaTreno non sono ufficiali e possono cambiare senza preavviso.
Il progetto è per uso personale e hobbistico.
