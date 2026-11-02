# Primo scambio commerciale con BAD

Obiettivo SAL 2: un contratto 2026 creato in Power Apps deve comparire in PostgreSQL.
I due CSV di questa cartella contengono solo le intestazioni di un **formato di
scambio proposto**, ricavato dallo schema SQL esistente. Non rappresentano un
export già verificato di Dataverse e non contengono vendite inventate.

## Prossimo passo con BAD

1. Creare un contratto di prova nell'ambiente del progetto, completo di righe.
2. Esportare contratto e righe, conservando gli identificativi Dataverse.
3. Confrontare i nomi reali delle colonne con queste intestazioni e registrare
   la mappatura. I GUID Dataverse non entrano direttamente in `id_contratto`
   (massimo 12 caratteri): concordare un codice commerciale stabile o una
   tabella di corrispondenza, senza troncare i GUID.
4. Verificare che espositore, stand ed edizione siano presenti in PostgreSQL.
   Per nuovi espositori servirà anche l'export anagrafico concordato.
5. Implementare il caricamento in un'unica transazione, con controlli prima
   della scrittura. Ripetere l'importazione deve aggiornare il medesimo
   contratto senza duplicarlo.
6. Confrontare contratto, righe e importi fra Power Apps, PostgreSQL e Power BI.

## Formato proposto

- CSV UTF-8 con intestazione, separatore virgola, testi con virgole tra doppi apici.
- Date `AAAA-MM-GG`; campi facoltativi vuoti; decimali con punto, senza simboli valuta.
- `sconto_pct` come frazione: `0.10` indica il 10%.
- `stato`: `preventivo`, `firmato`, `annullato`. Se firmato, `data_firma` obbligatoria.
- `rinnovo`: `true` oppure `false`.
- `riga`: numero positivo, univoco all'interno del contratto.
- Nessun secondo contratto non annullato per lo stesso stand nella stessa edizione.
- Non aggiungere nomi o email dei visitatori a questi export.

Il caricamento commerciale non è ancora implementato: serve un export reale
per verificare identificativi, relazioni e significato degli importi.
