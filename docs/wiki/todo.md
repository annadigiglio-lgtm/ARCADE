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
- [ ] Scegliere dove ospitare il DB condiviso (_da assegnare_)
- [ ] Decidere come arrivano nel DB i dati commerciali da Power Apps (BID + BAD)
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
