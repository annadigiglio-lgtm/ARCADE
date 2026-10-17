# 0004. Modello dati: tabelle pulite, decodifiche e anomalie con flag

- **Data:** 2026-10-17
- **Stato:** proposta (da discutere con BAD, da congelare al SAL 1)
- **Chi ha deciso:** BID

## Contesto

I dati arrivano da sistemi diversi con formati diversi tra il 2024 e il 2025 (tornelli in ora locale contro UTC, nomi dei biglietti e dei varchi cambiati, province scritte in tre modi, contratti 2024 senza codice espositore). Il cliente valuta che le anomalie siano "trovate e gestite" e che i numeri tornino tra le viste. Il modello deve servire sia lo storico sia i dati in diretta del 2026 (tornelli, app di scansione).

## Opzioni considerate

- **Correggere i dati a mano prima di caricarli:** veloce, ma non ripetibile e non dimostrabile al cliente.
- **Caricare i dati così come sono e pulirli nelle query:** ogni vista rifà la pulizia, con il rischio di numeri diversi.
- **Tabelle pulite con tabelle di decodifica e flag di anomalia:** la pulizia avviene una volta, al caricamento, ed è documentata nel DB.

## Decisione

- Tabelle pulite in un unico schema `arcade` (vedi [schema-dati.md](../schema-dati.md)).
- Le differenze di scrittura si risolvono con **tabelle di decodifica** (`*_alias`).
- Le righe anomale **non si cancellano**: si caricano con un flag e si escludono dai conteggi. Ogni anomalia è registrata nella tabella `anomalia` con il codice di [dati.md](../dati.md).
- Orari in `timestamptz`.
- Le assunzioni dei KPI stanno nella tabella `parametro`.

## Perché

- La pulizia è ripetibile: ricaricando i file si ottiene lo stesso risultato.
- Si può mostrare al cliente cosa è stato trovato e come è stato trattato.
- Lo stesso modello accoglie lo storico e i dati in diretta del 2026.

## Conseguenze

- Gli script di caricamento devono popolare le tabelle di decodifica e il registro anomalie.
- BAD scrive i contratti nelle stesse tabelle: i campi vanno concordati prima del SAL 1.
- Le tabelle di staging (dati grezzi) sono ancora da definire insieme all'ETL.
