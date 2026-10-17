# 0003. KPI calcolati una sola volta in viste SQL

- **Data:** 2026-10-17
- **Stato:** proposta (da concordare con BAD)
- **Chi ha deciso:** BID, in attesa di BAD

## Contesto

Un DB condiviso non basta a far tornare i numeri: se BID e BAD calcolano lo stesso KPI in modo diverso (es. visitatori = biglietti venduti oppure = ingressi ai tornelli), i risultati differiscono anche partendo dagli stessi dati.

## Opzioni considerate

- **Ognuno calcola i KPI nel proprio strumento** (Java per BID, DAX in Power BI per BAD): doppio lavoro e rischio di numeri diversi.
- **KPI calcolati in viste SQL nel DB** e usati da tutti: una sola definizione.

## Decisione

Ogni KPI ha una vista SQL nel DB (es. `v_kpi_visitatori`, `v_presenze_padiglione_ora`). Le API BID e Power BI leggono le stesse viste.

## Perché

- Un'unica definizione garantisce gli stessi numeri in tutte le viste.
- Se una definizione cambia, si modifica in un solo punto.
- Le viste documentano il calcolo e si possono mostrare al cliente.

## Conseguenze

- Le definizioni dei KPI vanno concordate prima di scrivere le viste (vedi [kpi.md](../kpi.md)).
- Power BI può ancora fare filtri e grafici, ma non deve ricalcolare i KPI.
- Le viste fanno parte dello schema e vanno versionate in `db/`.
