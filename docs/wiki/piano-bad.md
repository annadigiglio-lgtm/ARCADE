# Piano BAD fino al SAL del 4 dicembre

Aggiornato al 2026-11-23. Prossimo SAL: **venerdì 2026-12-04** ([programma](programma.md)); prova generale con BID **martedì 2026-12-01**. Obiettivo: chiudere tutto il lavoro BAD entro **lunedì 2026-11-30** e usare l'1–3/12 per prova generale, correzioni ed export finale. Le correzioni chieste da BID sono in [verifica-bad-2026-11-09.md](verifica-bad-2026-11-09.md).

Il lavoro rimasto è assegnato ad Alessandro; a fine settimana si spiega al resto del team cosa è stato fatto.

## Obiettivo del 4 dicembre

- App back-office con le correzioni di BID e una funzione in più per schermata ([idee](idee-miglioramento.md))
- App di scansione allo stand con QR code ([analisi](../../power-platform/app-scansione/README.md))
- Flussi obbligatori attivi nella soluzione e provati ([elenco e schede](../../power-platform/power-automate/README.md))
- Report Power BI con le 7 pagine, letto da PostgreSQL e raggiungibile dal back-office ([pagine](../../power-platform/powerbi/README.md))
- C2026-0200 e le scansioni dell'app in PostgreSQL, senza duplicati al secondo caricamento
- Stessi numeri in app, PostgreSQL, web e Power BI; demo prima / durante / dopo

## Stato al 2026-11-23

| Area | Fatto | Da fare |
|---|---|---|
| Soluzione Dataverse | 1.0.0.6 esportata e scompattata; 8 tabelle ([inventario](inventario-dataverse.md)) | export finale prima del 2026-12-15 (l'ambiente Developer viene sospeso) |
| Tabella scansioni | `g5_scansione_stand` ricreata il 2026-11-23 con 6 colonne e chiave ([procedura](../../power-platform/app-scansione/README.md#511-correzione-della-tabella-dellexport-1005)) | — |
| Flussi | 9 flussi attivi (FL-00…FL-08), una scheda per flusso | prove registrate nelle schede; correzioni elencate in "Da sistemare" |
| Report Power BI | `ARCADE-direzione.pbip` generato, si apre in Power BI Desktop | primo aggiornamento con la password di `bad_powerbi`, controllo dei numeri, pubblicazione |
| Back-office | app nella soluzione (versione del 2026-11-04) | correzioni di BID, pulsanti per FL-03 e FL-06, schermata Report |
| App di scansione | analisi e bozza grafica | tutta l'app |
| Integrazione con BID | importatori di BID pronti (`importa_commerciale.py`, `importa_scansioni.py`) | C2026-0200 e scansioni in PostgreSQL |
| Git | 4 commit sul branch `bad/aggiornato-16-novembre` | push e pull request verso `main` |

## Elenco del lavoro, in ordine

Ogni voce si chiude con una verifica scritta qui (data ed esito).

### 1. Dati commerciali in PostgreSQL

- [x] Chiarire i 206 contratti in Dataverse (attesi 201: 198 storici + C2026-0199, 0200, 0201). 2026-11-23: i 5 in più erano prove (C2026-9996…9999 dei flussi, C2026-10000 creato dall'app con la numerazione "massimo + 1"); annullati. Nessuno stand con due contratti non annullati nella stessa edizione.
- [x] FL-05: esportare solo i contratti e le righe dal 2026 (l'importatore di BID rifiuta lo storico) ([FL-05](../../power-platform/power-automate/FL-05.md)). 2026-11-23: filtri `anno ge '2026'` salvati nel flusso, provati sulla Web API (8 contratti, 36 righe).
- [x] CSV di C2026-0200 e delle sue righe nel [formato di scambio](../../power-platform/README.md#formato-proposto); validazione con `importa_commerciale.py`. 2026-11-23: letti da Dataverse (1 contratto, 4 righe, somma righe 10.838 = imponibile a listino), file in `power-platform/data/` (fuori da Git), validazione senza connessione superata.
- [ ] Import in PostgreSQL con Anna; secondo import senza duplicati
- [ ] C2026-0200 visibile in PB-04 e nel web

### 2. Back-office

- [ ] Panoramica: distinguere **prenotati** (contratti non annullati) e **venduti** (firmati), come nelle viste SQL
- [ ] Nuovo contratto: numero ed ID espositore non calcolati dal telefono; ricontrollo dello stand subito prima della scrittura; recupero se le righe non si salvano
- [ ] Contratti e Controlli: togliere il limite di 16 righe (`Sequence(16)`)
- [ ] Listino: modificare la voce cercando edizione **e** codice
- [ ] Pulsante "Invia preventivo" (FL-03) in Contratti e "Invia inviti" (FL-06) in Rinnovi
- [ ] Prova con due sessioni insieme e con un errore a metà salvataggio, esiti in [avanzamento.md](avanzamento.md)

### 3. App di scansione ARCADE Scan

- [ ] App Canvas (telefono) nella soluzione, `.msapp` in `power-platform/app-scansione/`
- [ ] Schermate: Inquadra QR, Elenco, Conta (+1), Senza rete, Riepilogo
- [ ] QR che apre direttamente lo stand (parametro nel link); salvataggio senza rete e invio al ritorno della rete
- [ ] PDF con i QR dei 130 stand (cartello A5)
- [ ] Ruolo di sicurezza ARCADE Scansione
- [ ] FL-05: file `scansione_stand.csv` nel formato di [import-scansioni.md](import-scansioni.md), con paginazione; import di BID senza duplicati

### 4. Flussi

- [ ] Prove di FL-01…FL-08 registrate nelle schede
- [ ] FL-03 e FL-06: risposta all'app anche in caso di errore
- [ ] FL-02: partire anche quando un contratto viene creato già firmato

### 5. Power BI

- [ ] Primo aggiornamento con la password di `bad_powerbi` (la dà Anna in privato)
- [ ] Controllo dei numeri delle 7 pagine con le viste SQL
- [ ] Pubblicazione nel servizio Power BI e schermata Report nel back-office (licenza da verificare)

### 6. Chiusura

- [ ] Numeri uguali in app, PostgreSQL, web e Power BI (tabella di confronto in [avanzamento.md](avanzamento.md))
- [ ] Push del branch e pull request verso `main`
- [ ] Assunzioni con ID univoci e separati dai codici delle anomalie di BID ([assunzioni-bad.md](assunzioni-bad.md))
- [ ] Prova generale con BID il 2026-12-01; correzioni il 2026-12-02; export finale di soluzione e report il 2026-12-03

## Calendario

| Giorno | Lavoro |
|---|---|
| lun 2026-11-23 | ✔ soluzione 1.0.0.6, schede dei flussi, report Power BI generato, tabella scansioni corretta |
| mar 2026-11-24 | 1. dati commerciali in PostgreSQL; push e pull request |
| mer 2026-11-25 | 2. correzioni del back-office |
| gio 2026-11-26 | 2. pulsanti dei flussi; 3. app di scansione (schermate) |
| ven 2026-11-27 | 3. QR, salvataggio senza rete, PDF dei QR, export delle scansioni |
| sab 2026-11-28 | 4. prove dei flussi; 5. Power BI collegato e controllato |
| dom 2026-11-29 | 5. pubblicazione e schermata Report; ruolo di sicurezza |
| lun 2026-11-30 | 6. verifica dei numeri, export della soluzione, documentazione |
| mar 2026-12-01 | **prova generale** con BID |
| mer 2026-12-02 | correzioni dalla prova; slide della demo |
| gio 2026-12-03 | export finale di soluzione e report, pull request, copia di sicurezza |
| **ven 2026-12-04** | **SAL** |
