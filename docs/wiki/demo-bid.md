# Demo BID — 16 novembre 2026

## Avvio e versione

L'app comprende cruscotto staff, confronto espositori, contatti consentiti e
proposta di rinnovo. Le modifiche API/web richiedono build e deploy insieme;
non servono ulteriori script SQL per questi endpoint: usano viste già pubblicate.
La simulazione legge lo storico, non crea eventi 2026 e non dimostra l'integrazione BAD.

Per avviare dal repository con le impostazioni Supabase private già presenti:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File api/avvia.ps1 -FileEnv .env.docker.local
```

Aprire `http://localhost:8080`. La sessione di verifica assistita del 16/11
usa invece `http://localhost:8082`; il processo deve essere in esecuzione.
Account demo e password nel file locale ignorato `api/demo-accounts.local`.
Non copiare password in slide, wiki, messaggi di gruppo o repository.
Su Render usare il servizio esistente `arcade-milano`, piano Free: **Manual Deploy →
Deploy latest commit**, dopo il push. Non creare nuovi servizi o database.
Controllare che il commit distribuito corrisponda alla versione da mostrare.

## Percorso della dimostrazione

1. Accedere come `staff.demo`. Spiegare l'istante mostrato e che le presenze
   sono una stima (permanenza proposta 120 minuti), non uscite rilevate.
2. Nei controlli storici scegliere 09:00 e mostrare il cruscotto, poi 11:55.
   Avviare la simulazione: +15 minuti ogni cinque secondi, oltre al caricamento.
   Mettere in pausa; a 19:00 si arresta automaticamente. Il grafico si ferma
   all'istante selezionato; l'intera demo non modifica lo storico.
3. Uscire e accedere come `espositore.demo1`. Mostrare il confronto 2024/2025:
   mq, imponibile, visite, contatti, ingressi al padiglione. Il trattino indica
   dato non rilevato; nel 2024 mancano le visite agli stand, non sono zero.
4. Selezionare 2025 per visite e contatti. Mostrare la paginazione dei soli
   contatti maggiorenni con consenso e email. Evitare proiezioni con email
   reali: per la presentazione fermarsi alla spiegazione o usare fixture locali.
5. Mostrare la stima rinnovo dell'edizione successiva all'ultimo contratto
   firmato: area/posizione, senza sconti o extra. Prezzi e prelazione sono
   proposte; il flag include preventivi e non prova una vendita firmata.
   Nessun pulsante conclude una prenotazione.
6. Uscire e accedere come `espositore.demo2`: verificare che gli stand siano
   diversi e che non restino dati del primo account. Provare anche il 2026:
   l'assenza di dati è coerente con il mancato export commerciale reale.

## Verifiche ripetibili

```powershell
node web/app.test.cjs
node api/verifica-condiviso.mjs http://127.0.0.1:8082
```

Il secondo comando usa gli account demo locali e controlla via HTTP tre login,
ruoli, visite/riepilogo, confronto/rinnovo, contatti paginati, tentativi di
cambiare identità via URL e istanti storici. Non stampa email, password o token.
Dopo il deploy usare `https://arcade-milano.onrender.com` al posto dell'URL locale.
Aprire in anticipo l'ambiente gratuito e verificare che sia pronto prima della demo.

Test privacy SQL: caricare schema e viste KPI in DB locale **vuoto di prova**,
poi `db/test_privacy_portale.sql`; i cinque contatti sono sintetici e il test
termina con ROLLBACK. Mai caricare fixture nel database condiviso.

## Stato e dipendenze

Verifiche del 16/11: nove test Java passati, privacy PostgreSQL verificata,
frontend verificato con DOM simulato e flussi HTTP locali su Supabase passati.
Il test frontend non certifica il layout desktop/mobile: revisione visiva aperta.
Deploy Render eseguito dall'utente e verificato via HTTPS il 16/11:
pagina/asset aggiornati, tre login, endpoint staff e portale, contatti paginati,
isolamento e simulazione superati. Nessuna scrittura DB durante la verifica.

Ancora necessari export commerciale/scansioni reali BAD, report Power BI,
conferma delle formule, condizioni rinnovo e importi incassati. Il contratto
C2026-0200 non era presente nell'ultima verifica; nessuna integrazione reale
2026 va dichiarata completata sulla base della simulazione.
