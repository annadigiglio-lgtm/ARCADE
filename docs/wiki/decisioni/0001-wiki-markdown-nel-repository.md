# 0001. Wiki in Markdown dentro il repository

- **Data:** 2026-10-17
- **Stato:** accettata
- **Chi ha deciso:** BID

## Contesto

Lavoriamo in due team, per sette settimane, con incontri in aula distanziati. Serve un posto unico dove trovare cosa c'è da fare, a che punto siamo e perché abbiamo fatto certe scelte, anche per spiegarle al cliente e in presentazione.

## Opzioni considerate

- **Wiki di GitHub:** comoda da modificare online, ma è un repository separato e non viaggia insieme al codice.
- **Documenti condivisi (Google Docs, Word):** facili da scrivere, ma fuori dal repository e senza storico legato al codice.
- **File Markdown in `docs/wiki/`:** versionati con il codice, leggibili su GitHub e in VS Code.

## Decisione

La wiki è una cartella `docs/wiki/` di file Markdown dentro il repository di progetto.

## Perché

- La consegna richiede un unico repository con tutta la documentazione.
- Le modifiche alla wiki hanno lo stesso storico di Git del codice.
- Si legge e si scrive con gli stessi strumenti che usiamo già.

## Conseguenze

- Ogni membro aggiorna la wiki insieme al lavoro che fa.
- Le decisioni importanti si registrano in `docs/wiki/decisioni/`.
