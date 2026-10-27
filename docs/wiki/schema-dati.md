# Schema dati

Stato: **bozza**, da discutere con BAD e congelare al SAL 1 (2026-10-30). Vedi [decisione 0004](decisioni/0004-modello-dati.md).

File SQL in `db/`:

| File | Contenuto |
|---|---|
| [`db/schema.sql`](../../db/schema.sql) | Tabelle, vincoli, indici |
| [`db/dati_base.sql`](../../db/dati_base.sql) | Edizioni, padiglioni, varchi, tipi biglietto, province, fasce d'età, parametri, tabelle di decodifica |
| [`db/viste_kpi.sql`](../../db/viste_kpi.sql) | Viste dei KPI (lette da Power BI e dalle API) |
| [`db/viste_api.sql`](../../db/viste_api.sql) | Funzioni del cruscotto e viste del portale espositori ([viste-api.md](viste-api.md)) |

> Gli script sono stati eseguiti con successo sul database condiviso Supabase il 2026-10-23: controllo superato (22 tabelle, 13 viste, dati di base completi). Dopo il caricamento dello storico ([guida](guida-caricamento.md)) le viste KPI danno gli stessi valori dell'analisi in [kpi.md](kpi.md). Le viste delle presenze stimate (`v_kpi_picco_*`) impiegano circa 6 secondi: per il cruscotto in diretta andranno ottimizzate (es. vista materializzata per le edizioni concluse).

## Diagramma

```mermaid
erDiagram
    EDIZIONE ||--o{ STAND : "attiva dal"
    EDIZIONE ||--o{ VOCE_LISTINO : "ha listino"
    EDIZIONE ||--o{ CONTRATTO : "per"
    EDIZIONE ||--o{ BIGLIETTO : "per"
    EDIZIONE ||--o{ TIPO_BIGLIETTO_ALIAS : "decodifica"
    EDIZIONE ||--o{ PASSAGGIO_VARCO : "per"
    EDIZIONE ||--o{ SCANSIONE_STAND : "per"
    EDIZIONE ||--o{ CONTATTO_STAND : "per"
    PADIGLIONE ||--o{ STAND : "contiene"
    PADIGLIONE ||--o{ VARCO : "servito da"
    ESPOSITORE ||--o{ ESPOSITORE_ALIAS : "nomi nelle fonti"
    ESPOSITORE ||--o{ CONTRATTO : "firma"
    ESPOSITORE ||--o{ CONTATTO_STAND : "raccoglie"
    ESPOSITORE o|--o{ UTENTE : "account espositore"
    STAND ||--o{ CONTRATTO : "venduto in"
    STAND ||--o{ SCANSIONE_STAND : "riceve"
    STAND ||--o{ CONTATTO_STAND : "raccoglie"
    CONTRATTO ||--|{ RIGA_CONTRATTO : "contiene"
    TIPO_BIGLIETTO ||--o{ TIPO_BIGLIETTO_ALIAS : "alias"
    TIPO_BIGLIETTO ||--o{ BIGLIETTO : "classifica"
    PROVINCIA ||--o{ PROVINCIA_ALIAS : "alias"
    PROVINCIA o|--o{ BIGLIETTO : "provenienza"
    PROVINCIA o|--o{ CONTATTO_STAND : "provenienza"
    FASCIA_ETA o|--o{ BIGLIETTO : "fascia"
    FASCIA_ETA o|--o{ CONTATTO_STAND : "fascia"
    BIGLIETTO ||--o{ PASSAGGIO_VARCO : "letto a"
    VARCO ||--o{ VARCO_ALIAS : "alias"
    VARCO ||--o{ PASSAGGIO_VARCO : "rileva"

    EDIZIONE {
        smallint anno PK
        date data_inizio
        date data_fine
    }
    PADIGLIONE {
        varchar codice PK
        text nome
    }
    STAND {
        varchar codice_stand PK
        varchar padiglione FK
        numeric mq
        varchar posizione
        smallint attivo_dal FK
    }
    ESPOSITORE {
        varchar id_espositore PK
        text ragione_sociale
        char partita_iva UK
        text referente_personale
        text email_referente_personale
    }
    ESPOSITORE_ALIAS {
        text nome_origine PK
        varchar id_espositore FK
    }
    VOCE_LISTINO {
        smallint edizione PK
        varchar codice PK
        numeric prezzo_unitario
    }
    CONTRATTO {
        varchar id_contratto PK
        smallint edizione FK
        varchar id_espositore FK
        varchar codice_stand FK
        text stato
        numeric imponibile
    }
    RIGA_CONTRATTO {
        varchar id_contratto PK,FK
        smallint riga PK
        numeric importo
    }
    TIPO_BIGLIETTO {
        varchar codice PK
        smallint persone
        smallint giorni
    }
    TIPO_BIGLIETTO_ALIAS {
        smallint edizione PK,FK
        text nome_origine PK
        varchar codice FK
    }
    PROVINCIA {
        char sigla PK
        text nome
    }
    PROVINCIA_ALIAS {
        text nome_origine PK
        char sigla FK
    }
    FASCIA_ETA {
        varchar codice PK
        boolean minorenne
    }
    BIGLIETTO {
        varchar id_biglietto PK
        smallint edizione FK
        varchar tipo FK
        varchar fascia_eta FK
        char provincia FK
    }
    VARCO {
        varchar codice PK
        varchar padiglione FK
    }
    VARCO_ALIAS {
        text nome_origine PK
        varchar codice FK
    }
    PASSAGGIO_VARCO {
        bigint id PK
        smallint edizione FK
        varchar codice_varco FK
        varchar id_biglietto FK
        boolean valido
    }
    SCANSIONE_STAND {
        bigint id PK
        smallint edizione FK
        varchar codice_stand FK
        integer quantita
    }
    CONTATTO_STAND {
        varchar id_contatto PK
        smallint edizione FK
        varchar codice_stand FK
        varchar id_espositore FK
        varchar fascia_eta FK
        char provincia FK
    }
    UTENTE {
        integer id PK
        text username UK
        text ruolo
        varchar id_espositore FK
    }
```

Il diagramma rappresenta le tabelle persistenti di `schema.sql`; staging, viste e funzioni sono oggetti tecnici e non entità del modello. Le relazioni opzionali verso `BIGLIETTO`, `PROVINCIA`, `FASCIA_ETA` e l'account espositore corrispondono a chiavi esterne ammesse a `NULL`. `RIGA_CONTRATTO` ha chiave composta (`id_contratto`, `riga`).

## Le tabelle in breve

### Dimensioni
| Tabella | Chiave | Note |
|---|---|---|
| `edizione` | anno | Date e orari della fiera (2024, 2025, 2026) |
| `padiglione` | codice (P1-P3) | |
| `stand` | codice_stand | mq, posizione, `attivo_dal` |
| `espositore` | id_espositore | Anagrafica, partita IVA unica |
| `voce_listino` | edizione + codice | Listino per edizione (abbiamo solo il 2026) |
| `tipo_biglietto` | codice | Tipo unico tra le edizioni, con persone e giorni |
| `provincia`, `fascia_eta` | sigla / codice | `fascia_eta.minorenne` serve per la tutela dei minori |
| `varco` | codice | Collegato al padiglione |

### Fatti
| Tabella | Una riga è | Chi la alimenta |
|---|---|---|
| `contratto` + `riga_contratto` | un contratto e le sue voci | BAD (storico da Excel, 2026 da Power Apps) |
| `biglietto` | un biglietto venduto | BID (CSV biglietteria) |
| `passaggio_varco` | una lettura al tornello | BID (CSV tornelli; in diretta per il 2026) |
| `scansione_stand` | N scansioni a uno stand in un istante | BID (storico orario 2025) e app di scansione BAD (2026) |
| `contatto_stand` | un contatto raccolto allo stand | BID (CSV) e app di scansione BAD |

### Decodifica e qualità
| Tabella | A cosa serve |
|---|---|
| `espositore_alias` | Ragione sociale scritta nei contratti → espositore (A16, A17) |
| `tipo_biglietto_alias` | Nome del tipo per edizione → tipo unico (A9) |
| `provincia_alias` | Sigla o nome maiuscolo → sigla (A10) |
| `varco_alias` | Nome del varco nelle fonti → codice (A3) |
| `anomalia` | Registro di tutte le anomalie trovate nel caricamento |
| `parametro` | Assunzioni dei KPI modificabili senza toccare il codice (permanenza, doppia lettura) |
| `utente` | Accesso alle interfacce; un utente `ESPOSITORE` è sempre legato alla sua azienda |

## Scelte principali

- **Due livelli**: i CSV si caricano prima in tabelle "grezze" (staging, da definire con l'ETL), poi nelle tabelle pulite qui sopra. Così il dato originale resta e la pulizia è ripetibile.
- **Le anomalie non si cancellano**: le righe dubbie si caricano con un flag (`passaggio_varco.anomalia`, `scansione_stand.anomalia`) e si escludono nei conteggi. Il campo calcolato `passaggio_varco.valido` dice se un passaggio conta.
- **Orari sempre con fuso** (`timestamptz`): risolve la differenza ora locale / UTC tra i tornelli 2024 e 2025.
- **Una tabella di scansioni per storico e diretta**: lo storico 2025 è aggregato per ora, l'app 2026 manderà scansioni singole. Il campo `quantita` copre entrambi i casi.
- **Uno stand venduto una sola volta per edizione**: indice unico su (edizione, stand) per i contratti non annullati.
- **Contratti con stato** (`preventivo`, `firmato`, `annullato`): serve per la fase "prima", dal preventivo al contratto.
- **Privacy nel DB, non solo nell'interfaccia**: la vista `v_contatti_espositore` mostra l'email solo con consenso e solo per i maggiorenni.

## Punti aperti

- [ ] Struttura delle tabelle di staging e script di caricamento
- [ ] Come BAD scrive i contratti 2026 (API o Power Automate): potrebbe richiedere campi in più (es. prelazione, solleciti)
- [ ] Sponsorizzazioni senza stand: oggi ogni contratto ha uno stand, va confermato
- [ ] Listini 2024 e 2025: non li abbiamo, i prezzi storici sono solo nelle righe dei contratti
