# Avanzamento

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
