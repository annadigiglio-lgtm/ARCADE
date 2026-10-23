# 0006. Database condiviso su Supabase

- **Data:** 2026-10-23
- **Stato:** accettata
- **Chi ha deciso:** BID

## Contesto

Il database PostgreSQL è il punto d'incontro tra BID e BAD ([decisione 0002](0002-database-condiviso.md)). Deve essere raggiungibile da tutti, anche da casa nelle settimane di lavoro autonomo, e da Power BI. Un database sul PC di uno di noi dipenderebbe da quel PC acceso e dalla rete della scuola.

## Opzioni considerate

- **PC di un membro del team** (rete locale o tunnel): fragile, il PC deve restare acceso.
- **Server della scuola**: non disponibile o non verificato.
- **Neon** (cloud gratuito): semplice; mette in pausa il calcolo dopo pochi minuti e lo riattiva alla prima connessione.
- **Supabase** (cloud gratuito): semplice, pannello web con editor SQL; mette in pausa il progetto dopo 7 giorni senza attività.

## Decisione

Il database condiviso è un progetto **Supabase** sul piano gratuito, in una regione europea. Per lo sviluppo ognuno usa PostgreSQL in locale con la stessa versione.

## Perché

- Gratuito e raggiungibile da ovunque, senza dipendere da un PC.
- Pannello web con editor SQL, comodo per chi non ha mai gestito un database in cloud.

## Conseguenze

- Istruzioni operative in [guida-supabase.md](../guida-supabase.md).
- Ci si collega tramite il **pooler in session mode** (IPv4); la connessione diretta richiede IPv6.
- Utenti distinti con permessi minimi: `bid_app` (lettura e scrittura), `bad_powerbi` (sola lettura).
- **Rischio pausa**: dopo 7 giorni senza attività il progetto si ferma; va controllato prima di ogni SAL e della demo.
- Il database deve restare ricostruibile da zero con gli script del repository.
