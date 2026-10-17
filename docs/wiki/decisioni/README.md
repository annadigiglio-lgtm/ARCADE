# Registro delle decisioni

Ogni decisione importante ha un file con il **contesto**, la **decisione** e le **conseguenze**. Formato ispirato agli Architecture Decision Records (ADR) di Michael Nygard.

## Quando scrivere una decisione

- Scelta di tecnologia o di architettura
- Struttura del DB o del contratto API
- Definizione di un KPI
- Come gestiamo un'anomalia dei dati
- Accordi con BAD o con il cliente

## Come si scrive

1. Copia [modello.md](modello.md) in un nuovo file `NNNN-titolo-breve.md` (numero progressivo).
2. Compila le sezioni e aggiungi una riga alla tabella qui sotto.
3. Le decisioni non si cancellano. Se una decisione cambia, se ne scrive una nuova e la vecchia diventa `sostituita da NNNN`.

Stati: `proposta` · `accettata` · `rifiutata` · `sostituita da NNNN`

## Elenco

| # | Decisione | Stato | Data |
|---|---|---|---|
| [0001](0001-wiki-markdown-nel-repository.md) | Wiki in Markdown dentro il repository | accettata | 2026-10-17 |
| [0002](0002-database-condiviso.md) | PostgreSQL condiviso come punto d'incontro BID/BAD | accettata | 2026-10-17 |
| [0003](0003-kpi-in-viste-sql.md) | KPI calcolati una sola volta in viste SQL | proposta | 2026-10-17 |
| [0004](0004-modello-dati.md) | Modello dati: tabelle pulite, decodifiche e anomalie con flag | proposta | 2026-10-17 |
