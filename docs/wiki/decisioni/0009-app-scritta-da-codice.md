# 0009. App back-office scritta da codice

- **Data:** 2026-11-03
- **Stato:** accettata
- **Chi ha deciso:** BAD

## Contesto

L'app Canvas si può costruire trascinando i controlli in Power Apps Studio oppure scrivendo le schermate in formato `.pa.yaml` e impacchettandole con `pac canvas pack`. L'app ha 9 schermate con molte formule ripetute (colori, intestazioni, menu, caricamento dei dati).

## Opzioni considerate

- **Solo Studio:** immediato per una schermata; le modifiche ripetute su 9 schermate si fanno a mano e non si vedono nel repository.
- **Generatore in Python che scrive i `.pa.yaml`:** più lavoro all'inizio; ogni modifica si fa in un punto solo e le versioni si confrontano in Git.

## Decisione

Le schermate nascono da `power-platform/canvas-src/genera_schermate.py`. Studio serve per aprire, provare, salvare e pubblicare, non per modificare le schermate.

## Perché

- Un menu, un colore o una regola si cambiano una volta sola per tutte le schermate.
- Il codice dell'app è leggibile nel repository e si può rivedere come quello di BID.

## Conseguenze

- Una modifica fatta a mano in Studio viene persa alla generazione successiva.
- Gli errori si leggono nel file `AppCheckerResult.sarif` del `.msapp` salvato da Studio ([guida](../guida-app-backoffice.md)).
