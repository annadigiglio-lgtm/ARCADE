# Cose da fare

## Aggiornamento 2026-11-02: Docker, Supabase e accesso da casa

- [x] Build del container Linux e cinque test Java superati.
- [x] Container avviato su localhost:8081 con limite 512 MB e DB Supabase.
- [x] Tre utenti demo su Supabase; login e ruoli verificati dal container.
- [x] SQL unico per le viste preparato e provato in locale con rollback.
- [x] `render.yaml` predisposto con un solo servizio gratuito e senza database Render.
- [x] Eseguire `db/pubblica_api_supabase.sql` con il proprietario dello schema.
- [x] Eseguire la verifica completa `node api/verifica-condiviso.mjs`.
- [ ] Autorizzare l'accesso a Render e pubblicare il codice del branch scelto.
- [ ] Pubblicare su Render Free e verificare l'URL HTTPS.

Dettagli: [render.md](render.md). Nessun deploy remoto ancora eseguito.

## Aggiornamento 2026-11-02: prima applicazione locale

- [x] Progetto Spring Boot con login, ruoli, endpoint staff, visite e riepilogo espositore.
- [x] Pagine locali per staff ed espositori, collegate alle API.
- [x] Tre utenti demo nel DB locale; verifica HTTP/SQL e test di isolamento superati.
- [x] Formato commerciale proposto in `power-platform/`, da verificare con BAD.
- [ ] Provare l'interfaccia nel browser e rivedere il codice insieme al team.
- [ ] Ottenere un export reale Dataverse e concordare mappatura e identificativi.
- [ ] Implementare l'importazione commerciale e provare il contratto 2026.
- [ ] Confrontare i numeri con Power BI e preparare l'ambiente condiviso.

Guida operativa: [`api/README.md`](../../api/README.md).
Le voci precedenti sotto non certificano lo stato del database condiviso.

Aggiornare a ogni sessione. Formato: `- [ ] attività (chi) — scadenza`. Quando è fatta, spuntarla e spostarla in fondo.

## Urgente (entro SAL 1, 2026-10-30)

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
- [ ] Utenti di demo nel DB: 1 staff e 2 espositori, password in BCrypt (Anna) — 2026-10-27
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
- [ ] Mappatura colonne Dataverse ↔ tabelle PostgreSQL (BID + BAD)
- [ ] Decidere come arriva lo storico commerciale 2024-2025 in Dataverse (BID + BAD)
- [ ] Ripensare il flusso delle scansioni dell'app di BAD senza chiamate alle API (BID + BAD)
- [ ] Preparare la presentazione del SAL 1 (tutti)

### Cliente
- [ ] Mandare le domande di [domande-cliente.md](domande-cliente.md) (team leader)

## Dopo il SAL 1

Dettaglio per area in [team.md](team.md#divisione-interna-bid).

- [ ] Anonimizzazione: niente nomi ed email esposti, minori solo aggregati (Anna) — SAL 2
- [ ] Caricamento dell'export commerciale da Dataverse (Anna) — SAL 2
- [x] API Spring Boot collegata a Supabase, endpoint principali, autenticazione e ruoli — verificato 2026-11-02
- [ ] Prima versione di cruscotto staff e portale espositori (Daniel) — SAL 2
- [ ] Isolamento espositori lato server (id dal token) (Yassin) — finale
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
