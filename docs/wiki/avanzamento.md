# Avanzamento

## 2026-11-16 — Revisione multi-stand verificata online

Deploy eseguito dall'utente; verifica HTTPS su Render superata dopo l'attesa
di avvio: asset aggiornati e riepiloghi multipli disponibili, limite UTF-8
corretto, tre login, portale, ruoli, isolamento e simulazione funzionanti.
Nessuna scrittura DB. Restano verifica visiva e dipendenze reali BAD/Power BI.

## 2026-11-16 — Revisione finale: multi-stand e casi limite

Corretto il riepilogo che prima restituiva solo il primo stand: endpoint plurale
e tabella dei riepiloghi per edizione, con costo per contatto da SQL.
L'endpoint singolo accetta selezione stand e restituisce 409 se ambiguo,
mantenendo compatibilità per un solo stand. Corretti limite UTF-8 del login,
schema nullable del picco ed errori 503 nella specifica. Il frontend pulisce
i risultati anche quando il caricamento fallisce.

12 test Java passati, test frontend ampliati e OpenAPI validato (11 percorsi).
Prova HTTP locale su Supabase passata con tre login, riepiloghi, isolamento,
contatti, rinnovo e simulazione. Nessuna scrittura su Supabase.
Report in `revisione-bid-2026-11-16.md`; nuovo deploy Render e verifica
visiva ancora aperti. Non dichiarata integrazione reale 2026 completata.

## 2026-11-16 — Deploy Render verificato via HTTPS

L'utente ha eseguito il deploy. Verifica su https://arcade-milano.onrender.com:
pagina e JavaScript aggiornati, tre login, quattro endpoint staff,
visite/riepilogo, confronto, rinnovo e contatti paginati tutti funzionanti.
Confermati isolamento dei due espositori, rifiuto di accessi non autorizzati
e parametri invalidi, identità dal token anche con ID diverso nell'URL.
Simulazione storica verificata via HTTP con istanti espliciti.
Nessuna scrittura DB durante le verifiche. Controllo visivo desktop/mobile
ancora aperto; export reali BAD e confronto nel report Power BI ancora necessari.

## 2026-11-16 — Portale, privacy e simulazione BID verificati

Completati pagina contatti paginati e rinnovo indicativo. Identità sempre dal
JWT, nessuna prenotazione o scrittura tramite il portale. Le stime di rinnovo
riguardano solo l'edizione successiva all'ultimo contratto firmato; il flag
comprende preventivi non annullati ed è spiegato nella pagina.
Cruscotto con simulazione storica del 20/12/2025, avanzamento di 15 minuti
ogni cinque secondi oltre al caricamento, pausa e ripristino ora servizio.
I quattro endpoint staff accettano lo stesso istante esplicito, senza scritture DB.

Verifiche: nove test Java superati; SQL privacy su PostgreSQL locale isolato
con cinque contatti sintetici e rollback; frontend con DOM simulato (NULL/zero,
testo sicuro, fine demo, pulizia logout e risposta di vecchia sessione);
HTTP locale su Supabase con tre login e tutti i nuovi endpoint, paginazione,
ruoli, tentativi di cambiare identità e simulazione. Campione tempi staff
124–481 ms su localhost (rete/Supabase inclusi), non benchmark di produzione.
OpenAPI YAML valido. Guida ripetibile in `demo-bid.md`.

Revisione visiva aperta: accesso browser non disponibile. Deploy Render aperto:
plugin trovato ma non collegato; richiesto collegamento, nessuna nuova risorsa
creata. Export reali BAD, report Power BI e conferme commerciali restano necessari.

## 2026-11-16 — Confronto tra edizioni nel portale espositori

Implementato `GET /espositore/me/confronto` sulla vista SQL già pubblicata,
con filtro espositore derivato dal JWT e ordinamento edizione/stand.
Aggiunta tabella al portale con mq, imponibile, visite, contatti e ingressi
al padiglione; supporta più stand e mantiene NULL distinto da zero.
La selezione edizione continua a filtrare le visite orarie, mentre il confronto
mostra tutte le edizioni disponibili. Nessuna modifica al database necessaria.

Verifica: sei test Java superati, compresi identità dal token, tentativo di
cambiare espositore via URL, risposte vuote e accessi vietati. Sintassi JS
e rendering DOM di NULL/zero/testo/stato vuoto verificati con Node.
Controllo visivo in browser e deploy Render ancora da effettuare.
Endpoint contatti e proposta di rinnovo ancora aperti. Nessun push o deploy.

## 2026-11-16 — Migrazione scansioni pubblicata su Supabase

Eseguita dall'utente; controllo successivo READ ONLY: colonna UUID presente,
indice univoco valido e CHECK NOT VALID nello stato previsto. Permessi INSERT
BID sulla tabella e sulla nuova colonna confermati. Storico presente: 2.451
righe 2025, 36.213 scansioni, ID 1–2.451 e GUID NULL; nessun evento app e
nessun UUID duplicato. Nessuna scrittura durante la verifica.
Restano conferma del GUID sorgente con BAD e prova dell'export reale.

## 2026-11-16 — Scansioni: migrazione e import verificati localmente

Preparati `db/migrazione_scansioni.sql`, schema per nuove installazioni e
`db/caricamento/importa_scansioni.py`, con CSV proposto a quattro colonne.
UUID univoco sorgente, quantità uno per nuovi eventi app, storico conservato;
reinvii identici ignorati e contenuti discordanti rifiutati in transazione.
Sei test superati, inclusa prova PostgreSQL isolata: migrazione ripetuta,
reimport, rollback FK/collisione e conservazione eventi legacy.
Nessuna modifica a Supabase. Pubblicazione ed export reale ancora aperti;
procedura in `import-scansioni.md`. Nessuna modifica a codice/app BAD.

## 2026-11-13 — Pubblicazione Supabase confermata e riconciliata

L'utente ha eseguito lo script nello SQL Editor. Verifica READ ONLY successiva:
quattro viste presenti e SELECT BAD confermato; rinnovo 2025 70/88 = 79,55%,
18 persi e 40 nuovi; conversione 96,44% nelle due edizioni storiche.
Totali giornalieri/canale riconciliati con biglietti e prezzi; conversione
riconciliata con passaggi validi distinti. Pagamenti: 198 righe, importi incassati
NULL. C2026-0200 ancora assente. Nessuna scrittura durante la verifica.
Il rinnovo 2026 resta parziale e non utilizzabile come risultato definitivo.
Dettagli in `avvio-power-bi.md`; login BAD e confronto nel report ancora aperti.

## 2026-11-13 — Viste Power BI implementate e verificate localmente

**Fatto:** aggiunte `v_kpi_rinnovo`, `v_incassi_contratto`,
`v_vendite_biglietti_giorno`, `v_kpi_conversione` a `db/viste_kpi.sql`.
Rinnovi per espositori distinti e contratti firmati; conversione per biglietti
con almeno un ingresso valido; vendite per data italiana e canale.
Incassi limitati allo stato registrato: importi effettivi non disponibili,
quindi `importo_incassato` NULL. Definizioni ancora proposte.
Rigenerato SQL di pubblicazione con permessi SELECT espliciti per BAD.

**Verifica:** PostgreSQL 18 isolato, schema reale e fixture sintetiche in
`db/test_viste_powerbi.sql`: duplicati, preventivi, rinnovi/persi/nuovi,
assenza storico, edizione senza biglietti, letture invalide, Family,
fuso italiano e stati pagamento. Fixture annullate tramite rollback.
Nessuna scrittura su Supabase e nessun deploy o push.

**Prossimi passi:** confermare definizioni e dati monetari con BAD,
pubblicare e verificare su Supabase, confrontare risultati storici e report.
Export commerciale reale ancora necessario per la prova 2026.

Diario del lavoro. Una voce per sessione, **la più recente in alto**.

Modello:

```
## AAAA-MM-GG — titolo breve
**Chi:** ...
**Fatto:** ...
**Problemi / dubbi:** ...
**Prossimi passi:** ...
```

---

## 2026-11-09 — Riscontro live alle domande BAD per avvio Power BI

**Fatto:** interrogato Supabase in transazione READ ONLY. Ruolo bad_powerbi
presente e SELECT sulle 17 viste attuali verificato tramite account BID.
C2026-0200 assente; le quattro viste richieste da BAD non esistono né nel DB
né nello script KPI; nessuna colonna UUID nella tabella scansioni. Entrambe
le copie locali dei CSV di scambio hanno zero record. Nessun ETL o DDL eseguito.

**Documentazione:** [avvio Power BI](avvio-power-bi.md), indice e TODO aggiornati.
Password BAD non recuperata o modificata; login BAD ancora da provare.


## 2026-11-09 — Nuova data SAL e preparazione import commerciale

**Aggiornamento dell’utente:** prossimo SAL il **4 dicembre 2026**; superata
la data del 13 novembre. Nessuna nuova data finale, presenza cliente o orario
sono stati comunicati. Aggiornati programma, ruoli, attività e revisione BAD.

**Fatto:** predisposto `db/caricamento/importa_commerciale.py`: valida i CSV
senza DB per impostazione predefinita; con `--applica` usa psql, transazione,
upsert contratti e sostituzione delle righe dei soli contratti inclusi.
Controlli su formato, importi, firma, duplicati e protezione dello storico.
Dieci test sintetici superati; inoltre import/reimport, rimozione di righe
obsolete e rollback su errore FK verificati su PostgreSQL 18 temporaneo,
poi arrestato. Nessun dato cliente usato nei test.
Aggiornate istruzioni Power Platform e stato della decisione 0005 con nota
operativa, senza attribuire al gruppo conferme ancora mancanti.

**Aperto:** export reale BAD e prova sul DB condiviso, correzioni nell’app BAD,
confronto Power BI e ripristino materiali presentazione mancanti dalla copia locale.
Mappatura commerciale riportata nella wiki per renderla consultabile senza
la cartella BAD separata; collegamenti a materiali mancanti sostituiti con
avvisi e attività di ripristino. Nessuna scrittura su database condivisi o
invio di messaggi al gruppo.

## 2026-11-09 — Verifica tecnica della consegna BAD e allineamento wiki

**Fatto:** confrontati documenti e sorgenti BAD con schema, viste KPI e formato
commerciale BID. Verificati ZIP 1.0.0.4 integro, 7 tabelle, 9 schermate, CSV
con zero record e assenza di file PBIX. Mappatura BAD ricevuta, ancora da
validare sull'export reale. Aggiornati indice, architettura e attività senza
modificare la consegna originale o i database.

**Problemi:** integrazione non dimostrata; differenza preventivi/firmati nel
conteggio dei venduti; rischio di salvataggio parziale e concorrenza; letture
su collezioni e limite di 16 righe; modifica listino senza edizione; assunzioni
con ID duplicati e abbinamenti 2024 ancora da confermare.

**Dettaglio e prossimi passi:** [verifica BAD](verifica-bad-2026-11-09.md).
Acquisire export di C2026-0200, validare mappatura, realizzare importazione
transazionale e idempotente, confrontare i KPI con BAD prima del SAL 2.
Prove live e conteggi dell'ambiente non rieseguiti in questa sessione.

## 2026-11-06 — Presentazione convertita in PDF

**Fatto:** dopo la segnalazione che il PowerPoint non si apre, creata una versione
PDF di cinque pagine in `output/pdf/ARCADE_Gruppo5_2026-11-06.pdf`, mantenendo
testi e grafici vettoriali. Le cinque pagine sono state renderizzate e controllate
visivamente; verificati numero di pagine e testi entro i limiti. Originali conservati.
Creata anche la scaletta integrale in tre pagine A4:
`output/pdf/ARCADE_Gruppo5_scaletta_2026-11-06.pdf`, renderizzata e verificata.

## 2026-11-06 — Analisi del pacchetto BAD e bozza di presentazione comune

**Fatto:** letta la cartella separata `ARCADE-BAD_2026-11-06` senza modificarla.
Il README BAD del 4/11 documenta soluzione Dataverse 1.0.0.4, 9 schermate Canvas
e 3 contratti 2026 di prova (C2026-0200 firmato, candidato SAL 2). Riscontrati
i 9 sorgenti delle schermate, il pacchetto soluzione, mappatura, Gantt HTML e
5 slide HTML BAD. Nessun `.pbix`; i due CSV di scambio contengono solo intestazioni.
Power Automate e app di scansione restano da fare secondo il report BAD.

Creata in `docs/presentazioni/stato-2026-11-06/` una bozza PowerPoint comune
di 5 slide: gruppo/ruoli, BID, BAD, integrazione, Gantt. Inclusi scaletta, inventario
e Gantt SVG. Date operative future indicate come proposta; il report BAD non
è stato trattato come prova live di sincronizzazione o come consegna originale.

**Verifiche:** struttura XML/ZIP e relazioni del PowerPoint, numero di slide,
forme entro la pagina, SVG e dati del Gantt validi. Nessun cambio ai database.

**Prossimi passi:** revisione del contenuto con BAD, conferma dei nomi e delle
date proposte, apertura e verifica visiva del PowerPoint prima dell'esposizione.

## 2026-11-02 — Guida di installazione per Yassin e Daniel

**Fatto:** aggiunta [ambiente-sviluppo.md](ambiente-sviluppo.md) con strumenti,
clone, passaggio privato delle credenziali, avvio Docker verso Supabase,
alternativa Java/JDK 21 per sviluppo API, aggiornamento delle pagine e controlli.
Documentata la differenza tra i file dotenv di Compose e quelli dello script Java,
la necessità di ricostruire il pacchetto dopo le modifiche e il deploy manuale
per aggiornare il sito pubblico. Collegamenti aggiunti a README, indice wiki,
team e guida API. Nessuna password aggiunta alla documentazione.

**Prossimi passi:** Yassin e Daniel installano gli strumenti sul proprio PC,
ricevono i parametri privati e verificano login e dati della propria copia.

## 2026-11-02 — Servizio Render pubblicato e verificato via HTTPS

**Fatto:** l'utente ha pubblicato il Blueprint su Render Free. URL confermato:
https://arcade-milano.onrender.com. Dopo consenso esplicito all'invio delle
credenziali demo al servizio, superata la verifica
`node api/verifica-condiviso.mjs https://arcade-milano.onrender.com`:
pagina/asset, tre login Supabase, quattro endpoint staff, visite e riepilogo
espositori, rifiuto di password/token errati e isolamento dei due account.
Non sono stati modificati dati durante la verifica.

**Prossimi passi:** prova visuale del gruppo nel browser; poi proseguire con
riepilogo completo nel portale ed export commerciale 2026 con BAD.

## 2026-11-02 — Viste Supabase pubblicate e verifica completa del container

**Fatto:** l'utente ha eseguito `db/pubblica_api_supabase.sql` nello SQL Editor
Supabase. `node api/verifica-condiviso.mjs` superato dal container su localhost:8081:
pagina/asset, tre login, quattro endpoint staff, visite/riepilogo espositori,
ruoli e isolamento dei due account. Il precedente blocco sulle viste è risolto.

**Prossimi passi:** autorizzare Render, pubblicare il codice aggiornato nel
repository scelto e completare il deploy Free con verifica dell'URL HTTPS.

## 2026-11-02 — Docker avviato con Supabase, preparazione Render Free

**Fatto:** build dell'immagine Linux riuscita con 5 test Java; container su
localhost:8081 con limite 512 MB; tre account demo creati e verificati su Supabase
senza sovrascrivere account esistenti. Pagina, asset, login, ruoli e credenziali
errate provati via HTTP. Preparati `avvia-docker.ps1`, verifica dell'ambiente
condiviso, SQL unico delle viste e Blueprint Render con un solo servizio Free.

**Blocco tecnico:** `bid_app` non ha CREATE sullo schema e le viste sono di
`postgres`. Lo SQL delle viste deve essere eseguito dal proprietario tramite
SQL Editor o collegamento Supabase autorizzato. Non tentato alcun aumento dei permessi.

**Prossimi passi:** pubblicare viste, verificare i dati dal container, autorizzare
Render e pubblicare il repository aggiornato, poi verificare il servizio HTTPS.
Nessun servizio Render creato. Dettagli in [render.md](render.md).

## 2026-11-02 — Prima applicazione locale staff ed espositori

**Chi:** sviluppo assistito con Codex, da rivedere insieme al team.

**Fatto:**

- Creato il progetto Spring Boot in `api/`: login BCrypt/JWT, ruoli STAFF ed
  ESPOSITORE, quattro endpoint staff, visite e riepilogo espositore.
- Aggiunte le pagine in `web/`, servite dall'API: login, presenze, riepilogo,
  andamento, ingressi orari e visite del proprio stand per edizione.
- Configurata la connessione con schema `arcade`. Nessuna ricreazione del DB
  e nessuna modifica applicata al database condiviso Supabase.
- Creati nel database locale tre utenti di demo: uno staff e due espositori.
  Password casuali nel file ignorato `api/demo-accounts.local`, hash BCrypt nel DB.
- Compilazione e 5 test automatici superati. Verifica HTTP contro PostgreSQL
  reale superata per pagina/asset, login, quattro endpoint staff, visite uguali
  a SQL, ruoli e isolamento tra espositori (`api/verifica-locale.mjs`).
- Preparato un formato CSV commerciale proposto e i punti da concordare con BAD
  in `power-platform/README.md`. Non ancora verificato con un export Dataverse.

**Limiti / prossimi passi:**

- Revisione del team su implementazione e contratto OpenAPI.
- Verifica visuale e interattiva in browser da completare.
- Orologio demo fisso al 20/12/2025 11:55, configurabile; polling ogni 30 s.
  Simulazione in movimento e soglie di capienza ancora da completare.
- Richiedere a BAD un export reale di contratto 2026 e righe, concordare
  identificativi e mappatura, implementare e verificare il caricamento.
- Confronto con Power BI e distribuzione condivisa da completare.
- Avvio e verifiche documentati in `api/README.md`.

## 2026-10-23 — Proposta viste per le API e database locale di prova

**Chi:** Anna

**Fatto:**

- Proposta delle viste lette dalle API per cruscotto e portale, da concordare con Yassin ([viste-api.md](viste-api.md))
- Database locale di prova sul PostgreSQL 18 del PC: `db/crea_db_locale.ps1` lo ricrea da zero con schema, viste e storico (28/28 controlli OK). `carica.ps1` ora accetta `-FileEnv .env.local` ([guida](guida-caricamento.md#database-locale-di-prova))

- Concordate con Yassin le convenzioni tra DB, API e web ([decisione 0007](decisioni/0007-convenzioni-api.md)): JSON in camelCase, JWT con id espositore nel token, polling ogni 30 s, ora simulata decisa dall'API per la demo
- Scritte e provate in locale `db/viste_api.sql`: 4 funzioni per il cruscotto (`presenze_al`, `andamento_al`, `ingressi_al`, `giornata_al`) e 4 viste per il portale; numeri coerenti con le viste KPI (0 differenze)
- Corretto in `v_permanenza` l'ordine dei passaggi nello stesso secondo, che rendeva il risultato non deterministico

**Prossimi passi:**

- Eseguire `viste_kpi.sql` e `viste_api.sql` su Supabase
- Utenti di demo nel database

## 2026-10-23 — Divisione dei compiti in BID

**Chi:** BID

**Fatto:**

- Assegnate le aree: DB ed ETL ad Anna, API a Yassin, Web a Daniel
- Scritti in [team.md](team.md#divisione-interna-bid) i compiti di ciascuno per SAL 1, SAL 2 e finale, e i passaggi di consegna tra le aree

**Prossimi passi:**

- Entro il 26/10: viste concordate (Anna + Yassin) e wireframe delle pagine (Daniel)
- Entro il 30/10: contratto OpenAPI (Yassin)

## 2026-10-23 — Prima riunione con tutto il gruppo

**Chi:** BID + BAD

**Fatto:**

- BAD non ha licenze Power Apps premium: niente connettori verso PostgreSQL o verso le API BID
- Deciso: BAD crea un ambiente Power Platform per il progetto e lavora su Dataverse; i dati commerciali vengono sincronizzati verso PostgreSQL; Power BI legge PostgreSQL ([decisione 0005](decisioni/0005-dataverse-sincronizzato-con-postgresql.md))
- Deciso: database condiviso su Supabase ([decisione 0006](decisioni/0006-supabase.md)); scritta la [guida](guida-supabase.md) per crearlo e collegarsi
- Creato il progetto Supabase, eseguiti `schema.sql`, `dati_base.sql`, `viste_kpi.sql` senza errori, creati gli utenti `bid_app` e `bad_powerbi`
- Query di controllo superata: 22 tabelle, 13 viste, dati di base completi
- Tutti i membri BID invitati nell'organizzazione Supabase
- Scritti gli script di caricamento in `db/caricamento/` ([guida](guida-caricamento.md)) e caricato lo storico 2024-2025 su Supabase: **28 controlli su 28 OK**, tutti i contratti 2024 abbinati, anomalie registrate nella tabella `anomalia`
- Viste KPI provate con i dati veri: stessi valori dell'analisi (es. saturazione 2025 70,8%, picco 2025 16.065 persone alle 11:55 di sabato)

**Problemi / dubbi:**

- Da definire chi fa la sincronizzazione e come ([architettura.md](architettura.md#sincronizzazione-dataverse--postgresql))
- Anche l'app di scansione di BAD non può chiamare le API BID: il flusso delle scansioni va ripensato

**Prossimi passi:**

- Scegliere la modalità di sincronizzazione e scrivere la mappatura con BAD
- Chiedere al tutor della registrazione dell'applicazione in Entra ID

## 2026-10-17 — Analisi dati, bozza schema e proposta KPI

**Chi:** Anna

**Fatto:**

- Analisi completa di tutti i file del cliente: 31 anomalie registrate con la gestione proposta e numeri di controllo per il caricamento ([dati.md](dati.md))
- Tutti i 88 contratti 2024 abbinati agli espositori tramite la ragione sociale (A16, A17); con l'abbinamento il flag `rinnovo` torna al 100%
- Bozza dello schema PostgreSQL: `db/schema.sql`, `db/dati_base.sql` ([schema-dati.md](schema-dati.md), [decisione 0004](decisioni/0004-modello-dati.md))
- Proposta di definizione dei 5 KPI con i valori 2024 e 2025, e bozza delle viste in `db/viste_kpi.sql` ([kpi.md](kpi.md))

**Risultati da segnalare:**

- Le "presenze" del brief corrispondono ai passaggi validi ai varchi senza doppie letture
- P2 (Esports & Community) è venduto per meno di un terzo, P1 e P3 sono pieni
- I varchi non registrano le uscite: il picco di presenza va stimato con un'assunzione sulla permanenza

**Problemi / dubbi:**

- Gli script SQL non sono ancora stati provati: PostgreSQL non è installato
- Nuove domande per il cliente (D10-D14)

**Prossimi passi:**

- Installare PostgreSQL ed eseguire gli script
- Discutere schema e KPI con Daniel, Yassin e BAD
- Progettare staging e script di caricamento

## 2026-10-17 — Lettura documenti e creazione wiki

Fatto:

- Letti il documento di progetto, il brief del cliente e l'elenco gruppi
- Prima occhiata ai dati: struttura dei file e prime anomalie ([dati.md](dati.md))
- Chiarita la divisione BID/BAD: il punto d'incontro è il DB condiviso, non le dashboard
- Creata questa wiki
  **Problemi / dubbi:**
- Date dell'edizione 2026 incoerenti tra documento del corso e brief  **Prossimi passi:**
- Dividere le aree all'interno di BID
- Riunione con BAD su KPI e integrazione
- Analisi completa dei dati

## 2026-10-16 — Kickoff

Fatto:

- Presentazione della fiera da parte del cliente, consegna dei dati
- Formazione dei team (Gruppo 5)
- Creato il repository con la struttura delle cartelle
