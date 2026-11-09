# Avvio Power BI — riscontro per BAD, 2026-11-09

Verifica eseguita su Supabase in transazione **READ ONLY**, con l'account BID
già configurato localmente. Nessuna modifica ai dati o allo schema.

## Connessione

- Server Session Pooler: `aws-1-eu-central-1.pooler.supabase.com`
- Porta: `5432`; database: `postgres`; SSL richiesto.
- Utente Power BI: `bad_powerbi.woomhgyyabzwkmbftkqo`.
- Schema da selezionare: `arcade`.

Il ruolo `bad_powerbi` esiste e ha SELECT sulle 17 viste attualmente presenti.
La verifica è stata fatta con l'account BID interrogando i permessi: non è
una prova di login con la password BAD. La password dedicata non è stata
recuperata né cambiata; va fornita in privato da chi la custodisce. Non usare
le credenziali BID per Power BI e non riportare password nella wiki.

## CSV e contratto 2026

I file `contratti-export.csv` e `righe-contratto-export.csv`, sia in
`ARCADE/power-platform/` sia nella consegna separata BAD, hanno **0 record**.
Il contratto `C2026-0200` non risulta nella tabella `arcade.contratto`.
La pipeline è disponibile e testata, ma manca l'export aggiornato con tutte
le righe del contratto; non è stata eseguita alcuna importazione vuota.
Istruzioni in [Power Platform](../../power-platform/README.md).

## Viste

Le viste KPI già documentate risultano pubblicate, ma **nessuna** di queste
quattro viste richieste è presente in Supabase o definita in `db/viste_kpi.sql`:

- `v_kpi_rinnovo`
- `v_incassi_contratto`
- `v_vendite_biglietti_giorno`
- `v_kpi_conversione`

Esiste `v_espositore_rinnovo`, che è una vista del portale e non va considerata
automaticamente equivalente a `v_kpi_rinnovo`. BAD può iniziare il collegamento
e i report sulle viste esistenti; le quattro estensioni richiedono definizioni
condivise, SQL, verifica dei risultati e pubblicazione con il proprietario dello
schema. Non sono state dichiarate disponibili prima della verifica.

## Scansioni

`arcade.scansione_stand` contiene `id bigint` e i campi di evento già previsti,
ma non contiene `g5_id_scansione` o altre colonne UUID. Anche `db/schema.sql`
non prevede ancora tale chiave. L'adeguamento non è quindi completato.
Va concordata e applicata una migrazione che conservi lo storico e imponga
l'unicità del GUID sorgente; il caricamento deve usare tale chiave per
riconoscere un evento già ricevuto. Il solo ID progressivo non dà idempotenza.

## Da completare per il prossimo SAL del 4 dicembre

1. Consegnare in privato la password BAD e provare il login da Power BI.
2. Ricevere i CSV con record e importare/verificare C2026-0200.
3. Definire, creare e pubblicare le quattro viste mancanti.
4. Concordare la chiave scansione e provare che il reinvio non duplichi l'evento.
