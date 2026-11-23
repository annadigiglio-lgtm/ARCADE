# 0008. Tabelle Dataverse con prefisso g5_, uguali allo schema SQL

- **Data:** 2026-11-03
- **Stato:** accettata
- **Chi ha deciso:** BAD

## Contesto

La prima versione delle tabelle era stata creata con il piano automatico di Power Apps (Plans). Le tabelle avevano il prefisso `cre10_` dell'editore predefinito, nomi diversi da `schema.sql` (es. `cre10_vocelistino`), una tabella in più (`cre10_visitastand`), mancava `riga_contratto` e `cre10_contratto` dava errore. Il prefisso di una tabella non si può cambiare dopo la creazione.

## Opzioni considerate

- **Tenere le tabelle `cre10_`:** nessun lavoro in più; nomi diversi da PostgreSQL, una tabella rotta e una mancante, mappatura più difficile.
- **Ricreare le tabelle con l'editore del team (prefisso `g5`)** partendo dalla specifica: un giorno di lavoro; nomi e colonne identici a `schema.sql`.

## Decisione

Le 7 tabelle commerciali sono nella soluzione **ARCADE BAD** con il prefisso `g5_` e gli stessi nomi di tabelle e colonne di `schema.sql`. La soluzione è generata dalla specifica [schema-dataverse.md](../schema-dataverse.md) con `power-platform/solution-src/genera_solution.py`.

## Perché

- La sincronizzazione verso PostgreSQL diventa una regola sola: togliere `g5_`.
- Le chiavi alternative sui codici (`g5_id_contratto`, `g5_codice_stand`…) permettono caricamenti ripetibili senza duplicati.

## Conseguenze

- Le tabelle `cre10_*` restano nell'ambiente, fuori dalla soluzione: non si sincronizzano. Eliminarle è da decidere (operazione che non si può annullare).
- Le colonne di Dataverse e PostgreSQL vanno tenute allineate: ogni modifica a `schema.sql` richiede la stessa modifica alla specifica e alla soluzione.
