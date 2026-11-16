# 0010. Le colonne data non si caricano con l'import Excel del portale

- **Data:** 2026-11-04
- **Stato:** accettata
- **Chi ha deciso:** BAD

## Contesto

Le edizioni sono state importate con *Importa dati da Excel* del portale Power Apps. Dopo l'import le date di inizio e fine delle tre edizioni risultavano indietro di un giorno (es. 17/12/2026 invece di 18/12/2026), per la conversione del fuso orario. Di conseguenza la scadenza del saldo di C2026-0200 era 17/11 invece di 18/11.

## Opzioni considerate

- **Correggere a mano nel portale:** veloce, ma il problema si ripresenta al prossimo import.
- **Caricare le date con la Web API di Dataverse**, in formato `AAAA-MM-GG` su colonne *Solo data*: nessuna conversione di fuso.

## Decisione

Le colonne data si caricano con la Web API in upsert sulla chiave alternativa. L'import Excel del portale si usa solo per tabelle senza date.

## Perché

- Le date sono identiche a PostgreSQL, quindi le scadenze calcolate dall'app tornano.

## Conseguenze

- Le tre edizioni e la scadenza del saldo di C2026-0200 sono state corrette il 2026-11-04 e confrontate con Supabase.
- Vale anche per l'export verso PostgreSQL: le date viaggiano come `AAAA-MM-GG` ([formato di scambio](../../../power-platform/README.md)).
