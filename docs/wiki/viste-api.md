# Viste lette dalle API

Stato: **concordato** tra DB e API il 2026-10-23 ([decisione 0007](decisioni/0007-convenzioni-api.md)). Da verificare con i wireframe di Daniel: se manca un numero si aggiunge qui.

SQL in [`db/viste_api.sql`](../../db/viste_api.sql). Le API non calcolano numeri: leggono queste viste e funzioni e le restituiscono ([decisione 0003](decisioni/0003-kpi-in-viste-sql.md)).

## Regole

- **Cruscotto: funzioni con l'istante come parametro** (`..._al(istante)`). In fiera l'istante è "adesso", nella demo è l'ora simulata decisa dall'API. Nessun numero guarda oltre quell'istante.
- **Portale: viste `v_espositore_*` con la colonna `id_espositore`**. L'API filtra sempre con `WHERE id_espositore = <id preso dal token>`, mai da un parametro dell'URL.
- **Nessun dato personale**: niente nomi né dati di singoli visitatori; le email solo tramite `v_contatti_espositore` (con consenso e solo maggiorenni).
- Nel DB i nomi sono in `snake_case`, l'API li restituisce in `camelCase`.

## Endpoint e fonti

### Cruscotto staff (ruolo `STAFF`)

| Endpoint | Fonte | Colonne | Mostra |
|---|---|---|---|
| `GET /affluenza/padiglioni` | `presenze_al(istante)` | `padiglione`, `nome_padiglione`, `presenti`, `istante` | Persone presenti ora in ogni padiglione |
| `GET /affluenza/andamento` | `andamento_al(istante)` | `istante`, `padiglione`, `presenti` | Curva della giornata ogni 5 minuti, dall'apertura a ora |
| `GET /affluenza/ingressi` | `ingressi_al(istante)` | `ora`, `padiglione`, `ingressi`, `persone` | Ingressi per ora e padiglione fino a ora |
| `GET /affluenza/giornata` | `giornata_al(istante)` | `giorno`, `visitatori`, `ingressi`, `picco_presenti`, `picco_istante` | Totali della giornata e picco raggiunto finora |

Esempio: `SELECT * FROM presenze_al('2025-12-20 11:55+01')` → P1 11.307, P2 3.140, P3 1.618 (totale 16.065, il picco 2025).

### Portale espositori (ruolo `ESPOSITORE`)

| Endpoint | Fonte | Colonne | Mostra |
|---|---|---|---|
| `GET /espositore/me/riepilogo?edizione=` | `v_espositore_riepilogo` | `id_espositore`, `edizione`, `ragione_sociale`, `codice_stand`, `padiglione`, `nome_padiglione`, `mq`, `posizione`, `imponibile`, `visite`, `contatti`, `contatti_con_consenso`, `costo_per_contatto`, `ora_di_punta`, `media_visite_padiglione` | Riepilogo di fine fiera, con la media del padiglione come termine di paragone |
| `GET /espositore/me/visite?edizione=` | `v_espositore_visite_ora` | `id_espositore`, `edizione`, `codice_stand`, `giorno`, `ora`, `scansioni` | Visite al proprio stand per giorno e ora |
| `GET /espositore/me/contatti?edizione=&page=&size=` | `v_contatti_espositore` | `id_contatto`, `id_espositore`, `edizione`, `codice_stand`, `raccolto_il`, `email`, `fascia_eta`, `provincia`, `interesse` | Contatti raccolti (paginati) |
| `GET /espositore/me/confronto` | `v_espositore_confronto` | `id_espositore`, `edizione`, `codice_stand`, `padiglione`, `mq`, `imponibile`, `visite`, `contatti`, `ingressi_padiglione` | Confronto tra edizioni |
| `GET /espositore/me/rinnovo` | `v_espositore_rinnovo` | `id_espositore`, `edizione_rinnovo`, `codice_stand`, `padiglione`, `mq`, `posizione`, `prezzo_area_stimato`, `prelazione_fino_al`, `gia_rinnovato` | Proposta di rinnovo sullo stesso stand |

Note:
- Visite e contatti esistono **solo dal 2025**: per il 2024 `visite`, `contatti` e `contatti_con_consenso` sono `NULL` ("non rilevati", non zero); nel confronto resta il traffico del padiglione.
- `media_visite_padiglione` è una media su tutti gli stand del padiglione: dato aggregato, non di un concorrente.
- `prezzo_area_stimato` = mq × prezzo al mq del padiglione (listino dell'edizione successiva) + maggiorazione di posizione; senza extra e prima degli sconti.

### Comune

| Endpoint | Fonte |
|---|---|
| `POST /auth/login` | tabella `utente` (password in BCrypt) |

## Verifiche fatte (database locale, 2026-10-23)

- `presenze_al` coincide con `v_presenze_stimate` in ogni istante di entrambe le edizioni (0 differenze).
- `giornata_al` a fine giornata dà gli stessi visitatori di `v_kpi_visitatori_giorno`.
- `costo_per_contatto` del riepilogo coincide con `v_kpi_costo_contatto` per tutti gli espositori.
- Somma delle visite in `v_espositore_visite_ora` = 35.301, come nel controllo del caricamento.
- Tempi in locale: `presenze_al` 0,4 s, `andamento_al` 0,8 s, `giornata_al` 1,1-1,3 s, viste del portale sotto 0,25 s.

## Da decidere

- **Soglia di affollamento** per gli avvisi del cruscotto: manca la capienza dei padiglioni, va chiesta al cliente e salvata nella tabella `parametro`.
