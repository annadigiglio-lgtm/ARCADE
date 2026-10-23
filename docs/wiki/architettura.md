# Architettura

Stato: **bozza**, da confermare con BAD entro il SAL 1 (2026-10-30).

## Idea centrale

Il **database PostgreSQL condiviso** è il punto d'incontro tra BID e BAD. Tutte le interfacce leggono dalla stessa fonte, e i KPI sono calcolati **una sola volta** dentro il DB (viste SQL), così i numeri coincidono ovunque. Vedi [decisione 0002](decisioni/0002-database-condiviso.md) e [decisione 0003](decisioni/0003-kpi-in-viste-sql.md).

BAD gestisce il back-office commerciale in **Dataverse** (ambiente Power Platform del progetto); i dati commerciali vengono copiati in PostgreSQL con una sincronizzazione. Vedi [decisione 0005](decisioni/0005-dataverse-sincronizzato-con-postgresql.md).

```
   CSV cliente                    Power Apps (BAD)
 (biglietti, tornelli, visite)          │
          │                        Dataverse (BAD)
          │                             │  sincronizzazione
          ▼  ETL (BID)                  ▼  (da definire)
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

## Sincronizzazione Dataverse → PostgreSQL

Senza licenze premium Power Automate non può chiamare le API BID (azione HTTP) né scrivere su PostgreSQL. Opzioni:

| Opzione | Chi | Come | Pro | Contro |
|---|---|---|---|---|
| **A. Lettura automatica dalle API Dataverse** | BID | Un job in Spring Boot legge ogni pochi minuti i record nuovi o modificati tramite la Web API di Dataverse e li scrive in PostgreSQL | Automatica, quasi in tempo reale | Serve una registrazione dell'applicazione in Microsoft Entra ID e un utente applicativo nell'ambiente: la scuola potrebbe bloccarla |
| **B. Esportazione e caricamento** | BAD esporta, BID carica | Export da Dataverse in CSV/Excel, poi lo script di caricamento BID lo importa | Nessun permesso speciale, stesso codice del caricamento storico | Manuale, dati aggiornati solo quando si esporta |

Proposta: scrivere il caricamento dei dati commerciali in modo che legga **lo stesso formato** sia dall'export (B) sia dall'API Dataverse (A). Si parte con B, che funziona sicuramente; se la registrazione dell'applicazione è possibile si passa ad A senza cambiare il resto.

## Punti aperti

- [x] Dove ospitare PostgreSQL: **Supabase**, piano gratuito ([decisione 0006](decisioni/0006-supabase.md), [guida](guida-supabase.md))
- [ ] Sincronizzazione Dataverse → PostgreSQL: scegliere tra A e B (sopra); verificare con il tutor se si può registrare un'applicazione in Entra ID
- [ ] Mappatura colonne Dataverse ↔ tabelle PostgreSQL, condivisa con BAD
- [ ] Formato e endpoint per le scansioni dell'app di BAD: l'app non può chiamare le API BID senza connettori premium, va ripensato (es. scansioni salvate in Dataverse e sincronizzate)
- [ ] Tempo reale per il cruscotto: polling periodico o Server-Sent Events
- [ ] Autenticazione: come riconoscere l'espositore e limitarlo ai propri dati
- [ ] I file del cliente contengono dati personali: decidere se versionarli su Git o tenerli fuori (`.gitignore`)

## Sicurezza e privacy (requisiti del cliente)

- **Isolamento espositori**: il filtro sull'espositore va applicato lato server (API/DB), mai solo nel frontend.
- **Minori** (fascia 14-17 e simili): niente dati identificativi esposti; usare solo dati aggregati.
- **Dati personali** (email, nomi): non esporli dove non servono; valutare pseudonimizzazione.
