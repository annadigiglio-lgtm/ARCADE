# Cose da fare

Aggiornare a ogni sessione. Formato: `- [ ] attività (chi) — scadenza`. Quando è fatta, spuntarla e spostarla in fondo.

## Urgente (entro SAL 1, 2026-10-30)

### Organizzazione
- [ ] Scegliere il team leader (tutti)
- [ ] Assegnare le aree BID: DB/ETL, API, Web (BID)
- [ ] Chiedere email di cliente e tutor (team leader)
- [ ] Riunione con BAD per KPI e integrazione (tutti)
### Dati
- [ ] Decidere se tenere i dati del cliente su Git o fuori (_da assegnare_)
- [ ] Rivedere in team le gestioni proposte delle anomalie in [dati.md](dati.md) (BID)

### Progettazione
- [ ] Installare PostgreSQL ed eseguire `db/schema.sql`, `db/dati_base.sql`, `db/viste_kpi.sql` (_da assegnare_)
- [ ] Concordare con BAD le definizioni dei KPI proposte in [kpi.md](kpi.md) (BID + BAD)
- [ ] Rivedere con BAD la bozza dello schema in [schema-dati.md](schema-dati.md) (BID + BAD)
- [ ] Progettare tabelle di staging e script di caricamento (_da assegnare_)
- [ ] Contratto API in OpenAPI (_da assegnare_)
- [ ] Cambiare le password di `bid_app` e `bad_powerbi` con due password diverse e robuste (responsabile DB)
- [ ] Mandare in privato a ogni membro BID l'host e la password di `bid_app`, e a BAD quella di `bad_powerbi` (responsabile DB)
- [ ] Installare un client (pgAdmin o DBeaver) e collegarsi con `bid_app` ([guida](guida-supabase.md#5b-collegarsi-per-la-prima-volta-ogni-membro-bid)) (ognuno)
- [ ] Mandare a BAD i dati di connessione per Power BI, in modo sicuro (responsabile DB)
- [ ] Scegliere la modalità di sincronizzazione Dataverse → PostgreSQL ([architettura.md](architettura.md#sincronizzazione-dataverse--postgresql)) (BID + BAD)
- [ ] Chiedere al tutor se si può registrare un'applicazione in Entra ID per leggere Dataverse (team leader)
- [ ] Mappatura colonne Dataverse ↔ tabelle PostgreSQL (BID + BAD)
- [ ] Decidere come arriva lo storico commerciale 2024-2025 in Dataverse (BID + BAD)
- [ ] Ripensare il flusso delle scansioni dell'app di BAD senza chiamate alle API (BID + BAD)
- [ ] Preparare la presentazione del SAL 1 (tutti)

### Cliente
- [ ] Mandare le domande di [domande-cliente.md](domande-cliente.md) (team leader)

## Dopo il SAL 1
- [ ] Script di caricamento 2024 e 2025
- [ ] Viste KPI
- [ ] API Spring Boot
- [ ] Cruscotto staff
- [ ] Portale espositori

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
