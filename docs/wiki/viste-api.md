# Viste lette dalle API

Stato: **proposta** (DB → API), da concordare tra Anna e Yassin entro il 2026-10-26 e da verificare con i wireframe di Daniel.

Le API non calcolano numeri: leggono queste viste e le restituiscono ([decisione 0003](decisioni/0003-kpi-in-viste-sql.md)). Se a una pagina manca un numero, si aggiunge una vista qui, non un calcolo in Java o in JavaScript.

## Regole

- **Nomi per pubblico**: `v_staff_*` per il cruscotto, `v_espositore_*` per il portale. I KPI della direzione (`v_kpi_*`) li legge Power BI.
- **Ogni vista `v_espositore_*` ha la colonna `id_espositore`**. L'API filtra sempre con `WHERE id_espositore = <id preso dal token>`, mai da un parametro dell'URL: così un espositore non vede i dati dei concorrenti.
- **Nessun dato personale** nelle viste per il web: niente nomi, email o dati di singoli visitatori, minori solo aggregati.
- Nomi delle colonne in `snake_case` nel DB; l'API può restituirli in `camelCase` nel JSON.
- Le funzioni con parametro (es. `presenze_al(istante)`) servono per la demo: permettono di "rivedere" una giornata del 2025 come se fosse in diretta.

## Cruscotto staff

| Vista / funzione | Colonne | Filtro dell'API | Mostra | Stato |
|---|---|---|---|---|
| `presenze_al(istante)` | `padiglione`, `nome_padiglione`, `presenti`, `istante` | istante = adesso (o ora simulata) | Persone presenti ora in ogni padiglione | da creare |
| `v_staff_andamento` | `edizione`, `giorno`, `istante`, `padiglione`, `presenti` | edizione, giorno | Curva delle presenze della giornata (ogni 5 min) | da creare, da `v_presenze_stimate` |
| `v_staff_ingressi_ora` | `edizione`, `giorno`, `ora`, `padiglione`, `ingressi`, `persone` | edizione, giorno | Ingressi per fascia oraria | da creare |
| `v_kpi_visitatori_giorno` | `edizione`, `giorno`, `visitatori`, `biglietti` | edizione, giorno | Visitatori della giornata | **esiste** |
| `v_kpi_picco_padiglione` | `edizione`, `padiglione`, `istante`, `presenti` | edizione | Picco dell'edizione, per confronto | **esiste** |

Da decidere: **soglia di affollamento** per gli avvisi. Non abbiamo la capienza dei padiglioni: va chiesta al cliente e salvata nella tabella `parametro`.

## Portale espositori

| Vista | Colonne | Filtro dell'API | Mostra | Stato |
|---|---|---|---|---|
| `v_espositore_visite_ora` | `id_espositore`, `edizione`, `codice_stand`, `giorno`, `ora`, `scansioni` | id dal token, edizione | Visite al proprio stand per giorno e ora | da creare, da `v_visite_stand_ora` + contratti |
| `v_espositore_riepilogo` | `id_espositore`, `edizione`, `ragione_sociale`, `codice_stand`, `padiglione`, `mq`, `visite`, `contatti`, `contatti_con_consenso`, `costo_per_contatto`, `ora_di_punta` | id dal token, edizione | Riepilogo di fine fiera | da creare |
| `v_espositore_confronto` | `id_espositore`, `edizione`, `codice_stand`, `mq`, `imponibile`, `visite`, `contatti`, `ingressi_padiglione` | id dal token | Confronto 2024/2025 | da creare |
| `v_contatti_espositore` | `id_contatto`, `id_espositore`, `edizione`, `raccolto_il`, `email` (solo con consenso e maggiorenni), `fascia_eta`, `provincia`, `interesse` | id dal token, edizione | Elenco dei contatti raccolti | **esiste** |
| `v_espositore_rinnovo` | `id_espositore`, `codice_stand`, `mq`, `posizione`, `prezzo_2026_stimato`, `prelazione_fino_al` | id dal token | Proposta di rinnovo sullo stesso stand | da creare |

Note:
- Visite e contatti esistono **solo per il 2025**: nel confronto il 2024 mostra solo i dati del contratto e gli ingressi del padiglione.
- Da decidere: mostrare all'espositore la **media del suo padiglione** (dato aggregato, non di un concorrente) come termine di paragone.
- `v_espositore_rinnovo` usa il listino 2026 (spazio al mq + maggiorazione di posizione) e la prelazione fino al 31 marzo 2026.

## Domande per la riunione

1. Gli endpoint del contratto OpenAPI corrispondono a queste viste? Ne manca qualcuna?
2. Il cruscotto chiede i dati ogni N secondi (polling) o in streaming? Cambia quanto devono essere veloci le viste.
3. Per la demo l'ora "attuale" la decide l'API (parametro di simulazione) o il DB?
4. Paginazione: l'elenco contatti può avere centinaia di righe per espositore.
