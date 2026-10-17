# Architettura

Stato: **bozza**, da confermare con BAD entro il SAL 1 (2026-10-30).

## Idea centrale

Il **database PostgreSQL condiviso** è il punto d'incontro tra BID e BAD. Tutte le interfacce leggono dalla stessa fonte, e i KPI sono calcolati **una sola volta** dentro il DB (viste SQL), così i numeri coincidono ovunque. Vedi [decisione 0002](decisioni/0002-database-condiviso.md) e [decisione 0003](decisioni/0003-kpi-in-viste-sql.md).

```
   CSV cliente                         Excel commerciale
 (biglietti, tornelli, visite)        + Power Apps (BAD)
          │                                   │
          ▼  ETL (BID)                        ▼  API o Power Automate
   ┌─────────────────────────────────────────────────────┐
   │        PostgreSQL – modello dati condiviso          │
   │   tabelle pulite  +  viste KPI (unica definizione)  │
   └─────────────────────────────────────────────────────┘
          │                                   │
   API Spring Boot (BID)                Power BI (BAD)
     │              │                         │
 Cruscotto staff  Portale espositori    Report direzione
     (BID)            (BID)                 (BAD)
                     ▲
          App scansione stand (BAD) ──► API (BID)
```

## Componenti

| Componente | Team | Cartella repo | Note |
|---|---|---|---|
| Schema e script DB | BID | `db/` | Tabelle, viste KPI, script di caricamento |
| Dati grezzi | — | `data/` | Copia dei file del cliente (attenzione ai dati personali, vedi sotto) |
| REST API | BID | `api/` | Java / Spring Boot, specifica OpenAPI |
| Interfacce web | BID | `web/` | Cruscotto staff, portale espositori |
| Power Platform | BAD | `power-platform/` | Power Apps, Power Automate, Power BI |
| Documentazione | tutti | `docs/` | Questa wiki |

## Punti aperti

- [ ] Dove ospitare PostgreSQL perché sia raggiungibile da tutti e da Power BI (cloud gratuito o server della scuola)
- [ ] Come arrivano nel DB i dati commerciali di Power Apps: scrittura via API BID o sincronizzazione da Dataverse con Power Automate
- [ ] Formato e endpoint per le scansioni dell'app di BAD
- [ ] Tempo reale per il cruscotto: polling periodico o Server-Sent Events
- [ ] Autenticazione: come riconoscere l'espositore e limitarlo ai propri dati
- [ ] I file del cliente contengono dati personali: decidere se versionarli su Git o tenerli fuori (`.gitignore`)

## Sicurezza e privacy (requisiti del cliente)

- **Isolamento espositori**: il filtro sull'espositore va applicato lato server (API/DB), mai solo nel frontend.
- **Minori** (fascia 14-17 e simili): niente dati identificativi esposti; usare solo dati aggregati.
- **Dati personali** (email, nomi): non esporli dove non servono; valutare pseudonimizzazione.
