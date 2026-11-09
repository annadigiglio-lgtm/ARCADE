# Programma

**Aggiornamento ricevuto il 2026-11-09: il prossimo SAL è il 2026-12-04.**
Il precedente riferimento al 13 novembre è superato. Il programma iniziale
prevedeva già una presentazione finale il 4 dicembre: contenuti e presenza del
cliente di quell'evento restano da riconfermare alla luce del nuovo calendario.
Non sono stati comunicati un nuovo orario o altri incontri.

## Milestone

| Data | Evento | Cliente | Cosa portare |
|---|---|---|---|
| ven 2026-10-16 | **Kickoff** | presente | Raccolta requisiti, consegna dati, formazione team ✅ |
| ven 2026-10-30 | **SAL 1** | presente | Analisi, processo, **schema dati** e **contratto API**. Schema e contratto vengono **congelati** |
| 2026-11-09 → 2026-12-03 | Preparazione del prossimo SAL | — | Integrazione commerciale, correzioni BAD, confronto KPI e prove demo |
| ven 2026-12-04 | **Prossimo SAL — nuova data confermata dall'utente** | da riconfermare | Due edizioni caricate, contratto 2026 end-to-end; preparare anche la demo prima/durante/dopo già prevista dal piano iniziale |

## Piano per fasi

### Fase 1: analisi e progettazione (fino al SAL 1, 2026-10-30)
- Analisi completa dei dati e registro anomalie ([dati.md](dati.md))
- Definizioni KPI concordate con BAD ([kpi.md](kpi.md))
- Schema dati (diagramma ER + script SQL)
- Contratto API (OpenAPI)
- Accordo con BAD su integrazione dati commerciali e app di scansione
- DB raggiungibile da tutti

### Fase 2: costruzione e integrazione (prossimo SAL, 2026-12-04)
- Script di caricamento per 2024 e 2025
- Viste KPI nel DB
- API principali funzionanti
- Prima versione di cruscotto staff e portale espositori
- Un contratto 2026 creato da Power Apps e visibile nel DB
- Import commerciale validato su export reale; reimport senza duplicati e rollback in caso di errore
- Distinzione tra stand prenotati e venduti firmati concordata con BAD

### Completamento e prove, in parallelo all'integrazione (entro 2026-12-04)
- Tempo reale nel cruscotto (simulazione dei passaggi ai varchi)
- Portale espositori completo: riepilogo, confronto, rinnovo
- Sicurezza: isolamento espositori, tutela minori
- Verifica che i numeri tornino tra web e Power BI
- README, specifica API, preparazione demo e presentazione

## Ordine operativo proposto

1. Subito: acquisire export BAD con record, verificare mappatura e correggere i problemi P1 della [revisione](verifica-bad-2026-11-09.md).
2. Integrare contratto e righe in un DB di prova; controllare FK, importi, ripetizione e fallimenti.
3. Collegare Power BI alle viste, confrontare i numeri e completare scansioni e simulazione.
4. Prima del 4/12: prova completa con ruoli diversi, controllo dell'ambiente condiviso e materiali di presentazione.

Questo ordine è una proposta operativa, non introduce scadenze intermedie concordate né invii automatici al cliente.
