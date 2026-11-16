# Piano BAD fino al SAL del 4 dicembre

Aggiornato al 2026-11-16. Il SAL del 13/11 è superato: il prossimo è **venerdì 2026-12-04** ([programma](programma.md)). Le correzioni chieste da BID sono in [verifica-bad-2026-11-09.md](verifica-bad-2026-11-09.md).

Sigle: **A** Alessandro (integrazione, app di scansione, coordinamento) · **L** Lorenzo (back-office: correzioni, planimetria, funzioni) · **Ad** Adam (flussi) · **C/Y** Cristian e Yenje (Power BI).

## Obiettivo del 4 dicembre

- App back-office con le correzioni di BID e una funzione in più per schermata ([idee](idee-miglioramento.md))
- App di scansione allo stand con QR code ([analisi](../../power-platform/app-scansione/README.md))
- Flussi obbligatori attivi nella soluzione ([elenco](../../power-platform/power-automate/README.md))
- Report Power BI con le 7 pagine, letto da PostgreSQL e raggiungibile dal back-office ([pagine](../../power-platform/powerbi/README.md))
- C2026-0200 e le scansioni dell'app in PostgreSQL, senza duplicati al secondo caricamento
- Stessi numeri in app, PostgreSQL, web e Power BI; demo prima / durante / dopo

## Settimana 1 — base solida e dati in PostgreSQL

| Giorno | A | L | Ad | C/Y |
|---|---|---|---|---|
| mar 17 | branch allineato a BID, push e pull request; export della soluzione; CSV di C2026-0200 ad Anna | correzioni di BID: prenotato/venduto, righe oltre 16, listino per edizione | flussi nell'export della soluzione; revisione | password `bad_powerbi`, collegamento, PB-01 |
| mer 18 | app di scansione v1 (schermate) | numerazione sicura e salvataggio con recupero | prove di FL-01 e FL-02; FL-05 nel formato di Anna | PB-02, PB-04 |
| gio 19 | scansione v2: QR che apre lo stand, salvataggio senza rete; QR in PDF per i 130 stand | planimetria isometrica v1 | FL-06, FL-03 (preventivo PDF) | PB-03, PB-05 |
| ven 20 | **integrazione 1:** C2026-0200 in PostgreSQL e in PB-04 (con Anna) | prove di concorrenza con due sessioni, esiti registrati | supporto all'integrazione | verifica dei numeri con Anna |

## Settimana 2 — funzioni complete

| Giorno | A | L | Ad | C/Y |
|---|---|---|---|---|
| lun 23 | export delle scansioni e import di BID senza duplicati | planimetria interattiva, stand alternativo | FL-04, FL-07 | PB-06, PB-07 |
| mar 24 | ruoli di sicurezza, utenti BID; schermata Report nel back-office | funzioni di Panoramica e Contratti | FL-08, variabili d'ambiente | pubblicazione nel servizio Power BI |
| mer 25 | funzioni di Nuovo contratto e Rinnovi | funzioni di Scadenze e Listino | prova completa dei flussi | rifinitura, pagine facoltative |
| gio 26 | vista 3D del padiglione (facoltativa) | funzioni di Espositori e Controlli dati | supporto alle prove | controllo dei KPI con le viste |
| ven 27 | **integrazione 2:** export completo, import di BID, numeri uguali in app, PostgreSQL, web e Power BI | | | |

## Settimana 3 — chiusura

| Giorno | Attività |
|---|---|
| lun 30 | correzioni; export della soluzione finale; documentazione |
| mar 1/12 | **prova generale** della demo con BID |
| mer 2/12 | correzioni dalla prova; slide della demo |
| gio 3/12 | export finale di soluzione e report, pull request, copia di sicurezza (l'ambiente viene sospeso dal 2026-12-15) |
| **ven 4/12** | **SAL** |

## Correzioni chieste da BID (verifica del 9/11)

- [ ] Panoramica: distinguere **prenotati** (contratti non annullati) e **venduti** (firmati), come la saturazione nelle viste SQL (L)
- [ ] Nuovo contratto: numero ed ID espositore non calcolati dal telefono; ricontrollo dello stand subito prima della scrittura; recupero se le righe non si salvano (L)
- [ ] Contratti e Controlli: togliere il limite di 16 righe (`Sequence(16)`) (L)
- [ ] Listino: modificare la voce cercando edizione **e** codice (L)
- [ ] Prova con due sessioni insieme e con un errore a metà salvataggio, esiti scritti in [avanzamento.md](avanzamento.md) (L)
- [ ] Assunzioni con ID univoci e separati dai codici delle anomalie di BID (A)
