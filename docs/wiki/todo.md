# Cose da fare

## Verifica pubblicazione Power BI — 13 novembre

- [x] Pubblicare le quattro nuove viste su Supabase (eseguito dall'utente) e verificare SELECT BAD, risultati storici e riconciliazione vendite/conversione in sola lettura.
- [ ] Provare il login Power BI con credenziali BAD e confrontare il report con i risultati in `avvio-power-bi.md`.
- [ ] Confermare le definizioni proposte e ricevere gli importi effettivi dei pagamenti; `importo_incassato` resta NULL.

La pubblicazione indicata ancora aperta nelle sezioni storiche sotto è completata;
restano aperte conferma delle formule e verifica nel report.

## Avvio Power BI — verifica live del 9 novembre

Riscontro: [avvio-power-bi.md](avvio-power-bi.md).

- [x] Verificare in sola lettura ruolo BAD e permessi sulle 17 viste presenti.
- [ ] Fornire in privato la password dedicata BAD e provare il login Power BI.
- [ ] Ricevere CSV con record: entrambe le copie locali sono ancora vuote; C2026-0200 assente da Supabase.
- [x] Implementare le quattro viste Power BI e provarle su PostgreSQL locale con dati sintetici (13/11); definizioni proposte in `kpi.md`.
- [ ] Confermare le formule, pubblicare le quattro viste su Supabase e confrontare lo storico con Power BI. Per gli incassi mancano gli importi effettivamente versati: la vista espone solo lo stato e importo NULL.
- [ ] Aggiungere la chiave UUID sorgente alle scansioni con vincolo univoco e caricamento idempotente; colonna non ancora presente.

## Verifica BAD — 9 novembre; priorità prossimo SAL del 4 dicembre

Dettagli e riferimenti: [verifica della consegna BAD](verifica-bad-2026-11-09.md).

- [x] Verificare struttura della consegna e confronto statico con modello e KPI BID.
- [x] Acquisire la mappatura documentale delle sette tabelle commerciali BAD.
- [ ] Ricevere export con record di C2026-0200 e righe, validare mappatura 1.0.0.4 e confermare opzione B (Anna + BAD).
- [x] Predisporre import commerciale transazionale e idempotente con validazione locale e test sintetici (9/11).
- [x] Provare su PostgreSQL 18 temporaneo import/reimport, rimozione righe obsolete e rollback FK (9/11; dati sintetici).
- [ ] Validare e provare export reale BAD sul DB di prova, poi applicare al DB condiviso (Anna).
- [ ] Separare stand prenotati da venduti firmati, confrontando le viste SQL (BAD + BID).
- [ ] Provare salvataggio parziale e due sessioni concorrenti su numeri e stand; correggere protezioni (BAD).
- [ ] Correggere selezione del listino per edizione/codice e rimuovere il limite implicito di 16 righe; verificare completezza delle collezioni (BAD).
- [ ] Rendere univoci gli ID delle assunzioni; confermare abbinamenti espositori 2024 e indice rinnovo (BAD + BID + cliente).
- [ ] Consegnare e confrontare report Power BI; completare flussi e app scansione con chiave stabile condivisa (BAD + BID).

## Presentazione comune — 6 novembre

- [x] Analizzare i materiali ricevuti da BAD e distinguere sorgenti, documenti e dati effettivi.
- [x] Preparare 5 slide comuni con presentazione del gruppo e Gantt sintetico.
- [ ] Rivedere con BAD stato e date del piano, confermare il nome di Yenje e controllare il PowerPoint nel programma di presentazione.

Materiali: la cartella `docs/presentazioni/stato-2026-11-06/` non è presente nella copia locale verificata.

- [ ] Ripristinare presentazione, scaletta e inventario del 6/11 e aggiornare il calendario dei materiali al 4/12.

## Ambiente di sviluppo del gruppo

- [x] Documentare installazione e primo avvio per Yassin e Daniel in [ambiente-sviluppo.md](ambiente-sviluppo.md).
- [ ] Installare gli strumenti, configurare i parametri privati e provare l'app sul proprio PC (Yassin).
- [ ] Installare gli strumenti, configurare i parametri privati e provare l'app sul proprio PC (Daniel).

## Aggiornamento 2026-11-02: Docker, Supabase e accesso da casa

- [x] Build del container Linux e cinque test Java superati.
- [x] Container avviato su localhost:8081 con limite 512 MB e DB Supabase.
- [x] Tre utenti demo su Supabase; login e ruoli verificati dal container.
- [x] SQL unico per le viste preparato e provato in locale con rollback.
- [x] `render.yaml` predisposto con un solo servizio gratuito e senza database Render.
- [x] Eseguire `db/pubblica_api_supabase.sql` con il proprietario dello schema.
- [x] Eseguire la verifica completa `node api/verifica-condiviso.mjs`.
- [x] Pubblicare il codice su GitHub e creare il servizio tramite il pannello Render (utente).
- [x] Pubblicare su Render Free e verificare l'URL HTTPS.

Dettagli: [render.md](render.md). Servizio verificato: https://arcade-milano.onrender.com.

## Aggiornamento 2026-11-02: prima applicazione locale

- [x] Progetto Spring Boot con login, ruoli, endpoint staff, visite e riepilogo espositore.
- [x] Pagine locali per staff ed espositori, collegate alle API.
- [x] Tre utenti demo nel DB locale; verifica HTTP/SQL e test di isolamento superati.
- [x] Formato commerciale proposto in `power-platform/`, da verificare con BAD.
- [ ] Provare l'interfaccia nel browser e rivedere il codice insieme al team.
- [ ] Ottenere un export Dataverse con record e validare la mappatura ricevuta il 9/11 e gli identificativi.
- [x] Implementare lo script di importazione commerciale sul formato CSV proposto (9/11).
- [ ] Provare il contratto 2026 con export reale e PostgreSQL.
- [ ] Confrontare i numeri con Power BI e preparare l'ambiente condiviso.

Guida operativa: [`api/README.md`](../../api/README.md).
Le voci precedenti sotto non certificano lo stato del database condiviso.

Aggiornare a ogni sessione. Formato: `- [ ] attività (chi) — scadenza`. Quando è fatta, spuntarla e spostarla in fondo.

## Attività residue dal SAL 1 (scadenza originaria 2026-10-30; riesame per il 04/12)

### Organizzazione
- [ ] Scegliere il team leader (tutti)
- [ ] Chiedere email di cliente e tutor (team leader)
- [ ] Riunione con BAD per KPI e integrazione (tutti)
### Dati
- [ ] Decidere se tenere i dati del cliente su Git o fuori (Anna)
- [ ] Rivedere in team le gestioni proposte delle anomalie in [dati.md](dati.md) (BID)

### Progettazione
- [ ] Concordare con BAD le definizioni dei KPI proposte in [kpi.md](kpi.md) (BID + BAD)
- [ ] Rivedere con BAD la bozza dello schema in [schema-dati.md](schema-dati.md) (BID + BAD)
- [ ] Rivedere in team gli script di caricamento in `db/caricamento/`: ognuno deve saperli spiegare (BID)
- [ ] Ottimizzare le viste delle presenze stimate per il cruscotto in diretta (~6 s oggi) (Anna)
- [x] Eseguire su Supabase `db/viste_kpi.sql` e `db/viste_api.sql` dall'SQL Editor (Anna) — completato 2026-11-02
- [x] Tre utenti demo su Supabase, login e ruoli verificati il 2/11.
- [ ] Verificare [viste-api.md](viste-api.md) con i wireframe di Daniel: se manca un numero, nuova vista (Anna + Daniel)
- [ ] Chiedere al cliente la capienza dei padiglioni per gli avvisi di affollamento (team leader)
- [ ] Wireframe di cruscotto staff e portale espositori, con i dati necessari in ogni pagina (Daniel) — 2026-10-26
- [ ] Scegliere la tecnologia del frontend e registrarla in `decisioni/` (Daniel)
- [ ] Contratto API in OpenAPI (Yassin) — 2026-10-30
- [ ] Validare e congelare con API e web il contratto in `api/openapi.yaml` (ruoli, trasporto e risposte) — 2026-10-30
- [x] Diagramma ER dello schema per il SAL 1 (Anna) - 2026-10-27
- [ ] Cambiare le password di `bid_app` e `bad_powerbi` con due password diverse e robuste (Anna)
- [ ] Mandare in privato a ogni membro BID l'host e la password di `bid_app`, e a BAD quella di `bad_powerbi` (Anna)
- [ ] Installare un client (pgAdmin o DBeaver) e collegarsi con `bid_app` ([guida](guida-supabase.md#5b-collegarsi-per-la-prima-volta-ogni-membro-bid)) (ognuno)
- [ ] Mandare a BAD i dati di connessione per Power BI, in modo sicuro (Anna)
- [ ] Scegliere la modalità di sincronizzazione Dataverse → PostgreSQL ([architettura.md](architettura.md#sincronizzazione-dataverse--postgresql)) (BID + BAD)
- [ ] Chiedere al tutor se si può registrare un'applicazione in Entra ID per leggere Dataverse (team leader)
- [x] Ricevuta mappatura documentale Dataverse/PostgreSQL; da validare su export reale (9/11).
- [x] Ricevuta descrizione caricamento storico in Dataverse (BAD, 3-4/11); conteggi non riverificati live.
- [ ] Ripensare il flusso delle scansioni dell'app di BAD senza chiamate alle API (BID + BAD)
- [ ] Preparare la presentazione del SAL 1 (tutti)

### Cliente
- [ ] Mandare le domande di [domande-cliente.md](domande-cliente.md) (team leader)

## Dopo il SAL 1

Dettaglio per area in [team.md](team.md#divisione-interna-bid).

- [ ] Anonimizzazione: niente nomi ed email esposti, minori solo aggregati (Anna) — prossimo SAL 04/12
- [ ] Caricamento dell'export commerciale da Dataverse (Anna) — prossimo SAL 04/12
- [x] API Spring Boot collegata a Supabase, endpoint principali, autenticazione e ruoli — verificato 2026-11-02
- [x] Prima versione web staff/espositore collegata alle API e verificata il 2/11; revisione visiva del gruppo ancora aperta.
- [x] Isolamento espositori lato server dal token implementato e verificato il 2/11.
- [ ] Tempo reale nel cruscotto (Yassin + Daniel) — finale
- [ ] Simulazione dei passaggi ai varchi e delle scansioni per la demo (Anna) — finale
- [ ] Portale completo: riepilogo, confronto 2024/2025, rinnovo (Daniel) — finale
- [ ] Verifica che web e Power BI diano gli stessi numeri (Anna + BAD) — finale

## Fatto
- [x] Kickoff e ricezione dati — 2026-10-16
- [x] Struttura iniziale del repository — 2026-10-16
- [x] Wiki di progetto — 2026-10-17
- [x] Analisi completa dei dati e registro anomalie — 2026-10-17
- [x] Bozza schema dati PostgreSQL — 2026-10-17
- [x] Proposta definizioni KPI con valori 2024/2025 — 2026-10-17
- [x] Scelto dove ospitare il DB condiviso: Supabase — 2026-10-23
- [x] Creato il progetto Supabase, eseguiti gli script in `db/` e creati gli utenti `bid_app` e `bad_powerbi` — 2026-10-23
- [x] Query di controllo del database superata — 2026-10-23
- [x] Membri BID invitati nell'organizzazione Supabase — 2026-10-23
- [x] Script di caricamento dello storico 2024-2025 e primo caricamento su Supabase (28/28 controlli OK) — 2026-10-23
- [x] Viste KPI provate con i dati veri — 2026-10-23
- [x] Database locale di prova (`db/crea_db_locale.ps1`, 28/28 controlli OK) — 2026-10-23
- [x] Viste e funzioni per le API concordate con Yassin, scritte e provate in locale (`db/viste_api.sql`) — 2026-10-23
- [x] Assegnate le aree BID: DB/ETL Anna, API Yassin, Web Daniel — 2026-10-23
