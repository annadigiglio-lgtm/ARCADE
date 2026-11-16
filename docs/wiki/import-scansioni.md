# Importazione scansioni app — 13 novembre 2026

Implementazione BID pronta per prova con export reale BAD. Il formato di scambio
è proposto: non certifica che tabella/app Dataverse siano già disponibili.
Nessun dato visitatore o biglietto è necessario nel CSV.

## Formato

CSV UTF-8, separatore virgola, intestazione esatta:

```csv
g5_id_scansione,edizione,codice_stand,rilevato_il
```

- GUID sorgente non nullo, creato una sola volta nell'app/Dataverse e conservato
  nei reinvii. Non generare un nuovo GUID durante ogni export.
- Edizione numerica dal 2026, codice stand PostgreSQL (massimo 10 caratteri).
- Timestamp ISO 8601 con secondi e fuso esplicito, ad esempio
  `2026-12-18T10:00:00+01:00` oppure `2026-12-18T09:00:00Z`.
- Una riga rappresenta un evento: l'import imposta `quantita=1`, `origine='app'`,
  nessuna anomalia. Lo storico orario resta separato.
- Esistenza di stand ed edizione verificata tramite FK nel DB. L'app deve
  autorizzare lo stand; il CSV non dimostra l'identità di chi ha scansionato.

## Pubblicazione della migrazione

Nel SQL Editor Supabase, come proprietario dello schema, eseguire **solo**
`db/migrazione_scansioni.sql`. Non eseguire `schema.sql` su un database popolato.
La migrazione è transazionale e rieseguibile: aggiunge UUID e indice univoco,
senza cambiare gli ID né cancellare righe. Gli UUID storici restano NULL.
Il vincolo per eventi app nuovi impone UUID e quantità uno; gli eventi app
preesistenti senza UUID sono conservati tramite CHECK NOT VALID. Non attribuire
GUID inventati allo storico e non reimportarlo come nuovi eventi app.
Il vincolo verrà validato integralmente solo dopo un'eventuale riconciliazione
degli eventi legacy con la sorgente.

## Uso

```powershell
python db/caricamento/importa_scansioni.py --scansioni "C:\export-privato\scansioni.csv"
```

Senza `--applica` valida solo il file, senza connessione o scrittura sul DB.
Per importare configurare PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD,
PGSSLMODE e PGCLIENTENCODING=UTF8 nella sessione privata; aggiungere
`--applica --psql "C:\Program Files\PostgreSQL\18\bin\psql.exe"`.
Non legge automaticamente i file `.env`. Usare il ruolo BID già autorizzato
alla scrittura, non le credenziali di sola lettura Power BI.

L'import è una transazione: reinvio dello stesso UUID e contenuto ignorato;
UUID con contenuto diverso rifiutato, senza aggiornare l'evento originale.
Duplicati identici nel CSV sono accorpati. Un errore FK o una collisione
discordante annulla tutto il batch. Le righe assenti dall'export non sono eliminate.
Un lock serializza gli import e le scritture concorrenti durante il batch;
timeout lock 10 s e istruzioni 60 s. Per volumi elevati suddividere gli export.
Le correzioni di eventi già ricevuti richiedono una procedura concordata,
non il cambio del GUID per aggirare il controllo.

## Verifiche

Test unitari:

```powershell
python -m unittest discover -s db/caricamento -p test_importa_scansioni.py -v
```

La suite include prova opzionale PostgreSQL su database **vuoto e isolato**:
impostare PG*, TEST_PSQL al percorso psql e SCANSIONI_TEST_DB=1.
Non abilitarla contro Supabase o un DB contenente dati: crea lo schema e fixture.
Copre reinvio, collisioni, rollback FK, conservazione storico e migrazione ripetuta.

Verifica PostgreSQL completata il 16/11: tutti i sei test superati, compresa
la prova integrata di migrazione/import su database isolato.

Stato: da pubblicare su Supabase; export reale e chiave sorgente da confermare
con BAD. Nessun evento sintetico va caricato nell'ambiente condiviso.
