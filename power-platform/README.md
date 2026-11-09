# Primo scambio commerciale con BAD

Obiettivo prossimo SAL, **4 dicembre 2026** (calendario aggiornato il 9/11):
un contratto 2026 creato in Power Apps deve comparire in PostgreSQL.
I due CSV di questa cartella contengono solo le intestazioni di un **formato di
scambio proposto**, ricavato dallo schema SQL esistente. Non rappresentano un
export già verificato di Dataverse e non contengono vendite inventate.

## Prossimo passo con BAD

1. Usare C2026-0200 come candidato: BAD lo dichiara già creato, firmato e pagato; resta un dato di prova.
2. Esportare contratto e tutte le righe, conservando separatamente gli identificativi Dataverse per tracciabilità.
3. Confrontare i nomi reali delle colonne con queste intestazioni e registrare
   la mappatura. I GUID Dataverse non entrano direttamente in `id_contratto`
   (massimo 12 caratteri): la mappatura ricevuta usa già il codice commerciale
   `C<anno>-<nnnn>`, da conservare senza troncare i GUID.
4. Verificare che espositore, stand ed edizione siano presenti in PostgreSQL.
   Per nuovi espositori servirà anche l'export anagrafico concordato.
5. Provare lo script di importazione sotto su un database di prova: controlli
   prima della scrittura, transazione unica e sostituzione completa delle righe
   dei soli contratti inclusi. Ripetere l'import non deve duplicare il contratto.
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

## Validazione e caricamento disponibili

Script: [`db/caricamento/importa_commerciale.py`](../db/caricamento/importa_commerciale.py),
Python standard library; per scrivere serve anche `psql`.

```powershell
python db/caricamento/importa_commerciale.py --contratti "C:\export-privato\contratti.csv" --righe "C:\export-privato\righe.csv"
```

Il comando predefinito valida i CSV senza collegarsi al DB. Rifiuta gli export
vuoti, duplicati, importi incoerenti e contratti anteriori al 2026; accetta
righe oltre la numero 16. Non importa le anagrafiche: espositore, edizione e
stand devono già esistere nel DB e saranno verificati dai vincoli PostgreSQL.

Per importare, configurare le variabili standard `PGHOST`, `PGPORT`,
`PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGSSLMODE`, `PGCLIENTENCODING=UTF8` in una
sessione privata, poi ripetere il comando aggiungendo `--applica`.
`--psql` permette di indicare il percorso dell'eseguibile se non è nel PATH.
Lo script non legge automaticamente i file `.env` e non stampa il contenuto
dei record o i dettagli SQL che possono contenere dati personali.

Ogni contratto incluso è uno **snapshot completo**: le sue righe precedenti
vengono sostituite. I contratti assenti dai CSV restano invariati; non si
deducono annullamenti dall'assenza. FK o collisioni con stand già occupati
fanno fallire tutta la transazione. L'import richiede anche i permessi di
lettura/scrittura sulle due tabelle e di creazione di tabelle temporanee.

Stato: validazione e generazione SQL provate localmente; esecuzione PostgreSQL
e compatibilità con export reale Dataverse ancora da verificare. Non usare i
CSV con sola intestazione come prova di integrazione riuscita.

Analisi dei problemi BAD: [verifica del 9/11](../docs/wiki/verifica-bad-2026-11-09.md).
