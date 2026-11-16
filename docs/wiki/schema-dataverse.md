# Specifica tabelle Dataverse – Solution `ARCADE_BAD`

Fonte di verità: [`db/schema.sql`](../../db/schema.sql) (descritto in [`wiki/schema-dati.md`](schema-dati.md)). Formato di scambio: [`power-platform/README.md`](../../power-platform/README.md).
Publisher prefix: **`g5`**. La sincronizzazione Dataverse → PostgreSQL è a senso unico, quindi nomi, tipi, vincoli e chiavi ricalcano lo schema SQL.

Le voci marcate **[verificare]** non sono certe: vanno controllate nel portale prima di fidarsi (sono raccolte anche in [`assunzioni-bad.md`](assunzioni-bad.md)).

---

## 1. Convenzioni (valgono per tutte le tabelle)

| Tema | Scelta | Perché |
|---|---|---|
| Nome logico tabella | `g5_` + nome SQL (es. `g5_voce_listino`) | Il prefisso del publisher è obbligatorio per gli oggetti custom |
| Nome logico colonna | `g5_` + nome SQL (es. `g5_partita_iva`) | Nome SQL riconoscibile nella mappatura Dataverse → PostgreSQL |
| Display name | Italiano, singolare (Edizione, Voce listino…); nome plurale impostato a mano | Lo vede l'utente nell'app |
| Proprietà del record | Tabella **di organizzazione** (non "di utente") | Nessuna gestione di proprietari e ruoli per record: sono tabelle di back-office condivise |
| Importi e percentuali | **Decimale**, non Valuta | Valuta aggiunge colonne di cambio che non servono e complicano l'export |
| Date | **Solo data** (comportamento *Date only*) | Niente fuso orario: la data scritta è la data esportata |
| Colonna primaria | Sempre testo (obbligo Dataverse). Si usa **una colonna già presente nello schema SQL**, non se ne aggiunge una apposta | Rispetta "non inventare colonne" |
| Chiave primaria SQL | In Dataverse ogni riga ha comunque un GUID di sistema. La chiave di business si riproduce con una **chiave alternativa** (unicità + upsert per chiave) | Dataverse non ha chiavi primarie composte |
| Colonne di sistema | `createdon`, `modifiedon`, `ownerid`, `statecode`, `statuscode`, ecc. e il GUID `g5_<tabella>id` esistono sempre: **non fanno parte dello schema SQL** e non vanno contate né esportate | Sono automatiche |
| CHECK con elenco chiuso | **Choice** locale, con etichette identiche ai valori SQL (minuscolo) | L'export dà la stessa stringa che PostgreSQL accetta |
| CHECK numerici | Valore minimo / massimo della colonna, quando basta | Dataverse li fa rispettare anche via API |
| Cancellazione | Relazioni di tipo *Referenziale, Restrict delete* (come una FK senza `ON DELETE`); solo `riga_contratto → contratto` è *Parentale* (cascade) | Replica `ON DELETE CASCADE` dello schema |

> `g5_stato` del contratto è una colonna nostra, diversa da `statecode`/`statuscode` di sistema (Attivo/Inattivo). Non vanno confuse né usate l'una al posto dell'altra.

---

## 2. Tabelle

Legenda "Obbl.": **Sì** = `NOT NULL` in SQL → in Dataverse *Business required*. Vedi la regola R5 (§4) sui limiti di questa obbligatorietà.

### 2.1 `g5_edizione` – Edizione

Colonna primaria: **`g5_anno`** (display "Anno"), testo 4 → corrisponde a `edizione.anno`.
Perché testo: la colonna primaria Dataverse deve essere testo, mentre in SQL `anno` è `smallint`. Il valore resta "2026" e la conversione a numero si fa alla sincronizzazione. Nell'app: `Value(g5_anno)` quando serve il numero.

| Colonna SQL | Colonna logica | Display | Tipo Dataverse | Obbl. | Vincoli / note |
|---|---|---|---|---|---|
| `anno` | `g5_anno` | Anno | Testo (riga singola), max 4, **primaria** | Sì | Chiave alternativa. 4 cifre (vedi R3b) |
| `data_inizio` | `g5_data_inizio` | Data inizio | Data e ora, comportamento *Solo data* | Sì | — |
| `data_fine` | `g5_data_fine` | Data fine | Data e ora, *Solo data* | Sì | `data_fine >= data_inizio` → regola R4 |
| `ora_apertura` | `g5_ora_apertura` | Ora apertura | Testo, max 5, formato `HH:MM` | Sì | Default `09:00`. Dataverse non ha il tipo "solo ora" → R6 |
| `ora_chiusura` | `g5_ora_chiusura` | Ora chiusura | Testo, max 5, formato `HH:MM` | Sì | Default `19:00` |

- **Chiavi alternative:** `KEY_edizione_anno` = (`g5_anno`).
- **Relazioni N:1:** nessuna.

### 2.2 `g5_padiglione` – Padiglione

Colonna primaria: **`g5_codice`** (display "Codice"), testo 2 → `padiglione.codice` (P1, P2, P3).

| Colonna SQL | Colonna logica | Display | Tipo Dataverse | Obbl. | Vincoli / note |
|---|---|---|---|---|---|
| `codice` | `g5_codice` | Codice | Testo, max 2, **primaria** | Sì | — |
| `nome` | `g5_nome` | Nome | Testo, max 100 | Sì | `UNIQUE` in SQL → chiave alternativa |

- **Chiavi alternative:** `KEY_padiglione_codice` = (`g5_codice`); `KEY_padiglione_nome` = (`g5_nome`).
- **Relazioni N:1:** nessuna.

### 2.3 `g5_espositore` – Espositore

Colonna primaria: **`g5_id_espositore`** (display "ID espositore"), testo 10 → `espositore.id_espositore` (es. ESP001).
Perché non `ragione_sociale` come primaria: l'import dello storico risolve le lookup sul nome primario, e i contratti portano `id_espositore`, non la ragione sociale. Nell'app si mostra comunque la ragione sociale.

| Colonna SQL | Colonna logica | Display | Tipo Dataverse | Obbl. | Vincoli / note |
|---|---|---|---|---|---|
| `id_espositore` | `g5_id_espositore` | ID espositore | Testo, max 10, **primaria** | Sì | — |
| `ragione_sociale` | `g5_ragione_sociale` | Ragione sociale | Testo, max 200 | Sì | Nessun UNIQUE in SQL |
| `partita_iva` | `g5_partita_iva` | Partita IVA | Testo, max 11 | Sì | 11 cifre e univoca → chiave alternativa + regola R3 per le cifre. **Mai** tipo numerico (perderebbe gli zeri iniziali) |
| `settore` | `g5_settore` | Settore | Testo, max 100 | No | — |
| `citta` | `g5_citta` | Città | Testo, max 100 | No | — |
| `referente` | `g5_referente` | Referente | Testo, max 200 | No | **Dato personale** |
| `email_referente` | `g5_email_referente` | Email referente | Testo, max 200 (formato Email) | No | **Dato personale** |

- **Chiavi alternative:** `KEY_espositore_id` = (`g5_id_espositore`); `KEY_espositore_piva` = (`g5_partita_iva`).
- **Relazioni N:1:** nessuna.
- Fuori scopo: `espositore_alias` (decodifica dei nomi nelle fonti, la gestisce BID nel caricamento).

### 2.4 `g5_stand` – Stand

Colonna primaria: **`g5_codice_stand`** (display "Codice stand"), testo 10 → `stand.codice_stand` (es. P1-A01).
**Nessuna colonna "stato"** (libero/occupato): si deriva dai contratti non annullati dell'edizione (§4, R1).

| Colonna SQL | Colonna logica | Display | Tipo Dataverse | Obbl. | Vincoli / note |
|---|---|---|---|---|---|
| `codice_stand` | `g5_codice_stand` | Codice stand | Testo, max 10, **primaria** | Sì | — |
| `padiglione` | `g5_padiglione` | Padiglione | **Lookup** → `g5_padiglione` | Sì | Vedi relazioni |
| `mq` | `g5_mq` | Metri quadri | Decimale, precisione 1, minimo **0,1**, massimo 99999,9 | Sì | `CHECK (mq > 0)`: con precisione 1 il minimo 0,1 equivale a "> 0" |
| `posizione` | `g5_posizione` | Posizione | **Choice** locale: `linea`, `angolo`, `penisola`, `isola` | Sì | Replica il CHECK. Nessun default |
| `attivo_dal` | `g5_attivo_dal` | Attivo dal | **Lookup** → `g5_edizione` | Sì | In SQL è un `smallint` FK a `edizione.anno` |

- **Chiavi alternative:** `KEY_stand_codice` = (`g5_codice_stand`).
- **Relazioni N:1:**
  - `g5_stand` → `g5_padiglione`, lookup **`g5_padiglione`** (nome relazione `g5_padiglione_g5_stand`), Restrict delete.
  - `g5_stand` → `g5_edizione`, lookup **`g5_attivo_dal`** (`g5_edizione_g5_stand_attivo_dal`), Restrict delete.

### 2.5 `g5_voce_listino` – Voce listino

Colonna primaria: **`g5_codice`** (display "Codice"), testo 20 → `voce_listino.codice` (es. SPAZIO-P1, MAGG-ANGOLO, SP-STAGE).
La chiave SQL è composta (`edizione`, `codice`): lo stesso codice può esistere in edizioni diverse, quindi il codice da solo **non** è univoco; lo è con l'edizione.

| Colonna SQL | Colonna logica | Display | Tipo Dataverse | Obbl. | Vincoli / note |
|---|---|---|---|---|---|
| `edizione` | `g5_edizione` | Edizione | **Lookup** → `g5_edizione` | Sì | — |
| `codice` | `g5_codice` | Codice | Testo, max 20, **primaria** | Sì | — |
| `descrizione` | `g5_descrizione` | Descrizione | Testo, max 500 | Sì | — |
| `unita` | `g5_unita` | Unità | Testo, max 50 | No | — |
| `prezzo_unitario` | `g5_prezzo_unitario` | Prezzo unitario | Decimale, precisione 2 | No | `numeric(10,2)`: massimo 99999999,99. Nullable in SQL (voce senza prezzo) |
| `disponibilita` | `g5_disponibilita` | Disponibilità | Numero intero | No | **Vuoto = illimitata / da planimetria.** Non mettere 0 al posto del vuoto |
| `note` | `g5_note` | Note | Testo, max 1000 (area di testo) | No | — |

- **Chiavi alternative:** `KEY_voce_listino` = (`g5_edizione`, `g5_codice`) – composta, con la lookup.
- **Relazioni N:1:** `g5_voce_listino` → `g5_edizione`, lookup **`g5_edizione`** (`g5_edizione_g5_voce_listino`), Restrict delete.

### 2.6 `g5_contratto` – Contratto

Colonna primaria: **`g5_id_contratto`** (display "ID contratto"), testo 12 → `contratto.id_contratto` (es. C2026-0001). Sul formato dell'ID vedi §3.

| Colonna SQL | Colonna logica | Display | Tipo Dataverse | Obbl. | Vincoli / note |
|---|---|---|---|---|---|
| `id_contratto` | `g5_id_contratto` | ID contratto | Testo, max 12, **primaria** (oppure Autonumber, §3) | Sì | — |
| `edizione` | `g5_edizione` | Edizione | **Lookup** → `g5_edizione` | Sì | — |
| `id_espositore` | `g5_espositore` | Espositore | **Lookup** → `g5_espositore` | Sì | Il valore esportato è `g5_id_espositore` |
| `codice_stand` | `g5_stand` | Stand | **Lookup** → `g5_stand` | Sì | Il valore esportato è `g5_codice_stand` |
| `stato` | `g5_stato` | Stato | **Choice** locale: `preventivo`, `firmato`, `annullato` | Sì | Default SQL = `firmato`. Vedi assunzione A3 |
| `data_firma` | `g5_data_firma` | Data firma | Data e ora, *Solo data* | No (ma Sì se firmato) | `stato = firmato ⇒ data_firma` → regola R2 |
| `imponibile_listino` | `g5_imponibile_listino` | Imponibile a listino | Decimale, precisione 2, minimo **0**, massimo 9999999999,99 | Sì | `CHECK >= 0` coperto dal minimo |
| `sconto_pct` | `g5_sconto_pct` | Sconto | Decimale, precisione **4**, minimo **0**, massimo **1** | Sì | Frazione (`0.10` = 10%). Default SQL 0: Dataverse non assegna default ai decimali → lo imposta il wizard (R7) |
| `imponibile` | `g5_imponibile` | Imponibile | Decimale, precisione 2, minimo **0**, massimo 9999999999,99 | Sì | — |
| `acconto_scadenza` | `g5_acconto_scadenza` | Scadenza acconto | Data e ora, *Solo data* | No | — |
| `acconto_pagato_il` | `g5_acconto_pagato_il` | Acconto pagato il | Data e ora, *Solo data* | No | — |
| `saldo_scadenza` | `g5_saldo_scadenza` | Scadenza saldo | Data e ora, *Solo data* | No | — |
| `saldo_pagato_il` | `g5_saldo_pagato_il` | Saldo pagato il | Data e ora, *Solo data* | No | — |
| `rinnovo` | `g5_rinnovo` | Rinnovo | Sì/No (Two options), default **No** | Sì | Default SQL `false` |

- **Chiavi alternative:** `KEY_contratto_id` = (`g5_id_contratto`).
  Nessuna chiave alternativa su (edizione, stand): in PostgreSQL l'indice è **parziale** (solo non annullati), Dataverse non può farlo → regola R1.
- **Relazioni N:1:**
  - `g5_contratto` → `g5_edizione`, lookup **`g5_edizione`** (`g5_edizione_g5_contratto`), Restrict delete.
  - `g5_contratto` → `g5_espositore`, lookup **`g5_espositore`** (`g5_espositore_g5_contratto`), Restrict delete.
  - `g5_contratto` → `g5_stand`, lookup **`g5_stand`** (`g5_stand_g5_contratto`), Restrict delete.

### 2.7 `g5_riga_contratto` – Riga contratto

Colonna primaria: **`g5_descrizione`** (display "Descrizione"), testo 500 → `riga_contratto.descrizione`.
Perché: la chiave SQL è (`id_contratto`, `riga`), composta, senza un testo unico che faccia da nome. `descrizione` è già `NOT NULL` nello schema e descrive la riga, quindi fa da colonna primaria senza aggiungere colonne.

| Colonna SQL | Colonna logica | Display | Tipo Dataverse | Obbl. | Vincoli / note |
|---|---|---|---|---|---|
| `id_contratto` | `g5_contratto` | Contratto | **Lookup** → `g5_contratto` | Sì | Relazione **Parentale** (cascade delete) |
| `riga` | `g5_riga` | Riga | Numero intero, minimo **1**, massimo 32767 | Sì | `smallint`; il minimo 1 è una cautela: SQL non ha CHECK su `riga` (assunzione A5) |
| `codice_voce` | `g5_codice_voce` | Codice voce | Testo, max 20 | Sì | **Non è una lookup** su `g5_voce_listino`: lo storico usa SPAZIO, MAGG, EX-*, SP-* che non esistono nel listino |
| `descrizione` | `g5_descrizione` | Descrizione | Testo, max 500, **primaria** | Sì | — |
| `quantita` | `g5_quantita` | Quantità | Decimale, precisione 2, minimo **0,01**, massimo 99999999,99 | Sì | `CHECK (quantita > 0)`: con precisione 2 il minimo 0,01 equivale a "> 0" |
| `prezzo_unitario` | `g5_prezzo_unitario` | Prezzo unitario | Decimale, precisione 2 | Sì | `numeric(12,2)`; SQL non vieta valori negativi, quindi **nessun minimo** |
| `importo` | `g5_importo` | Importo | Decimale, precisione 2 | Sì | idem |

- **Chiavi alternative:** `KEY_riga_contratto` = (`g5_contratto`, `g5_riga`) – composta, con la lookup.
- **Relazioni N:1:** `g5_riga_contratto` → `g5_contratto`, lookup **`g5_contratto`** (`g5_contratto_g5_riga_contratto`), **Parentale** (Delete: cascade). Replica `ON DELETE CASCADE`.

---

## 3. Formato dell'ID contratto (da decidere prima della Fase 2)

Opzioni:

| | A. Testo normale (scelta di partenza) | B. Autonumber `C2026-{SEQNUM:4}` |
|---|---|---|
| Lunghezza | `C2026-0001` = 10 caratteri, entro 12 | 10 caratteri, entro 12 |
| Storico (C2024-xxxx, C2025-xxxx) | Si importa com'è | **[verificare]** se un import accetta valori espliciti nell'Autonumber; il prefisso `2026` è fisso nel formato |
| Nuovi contratti | L'ID lo genera il wizard (ultimo numero + 1) | Lo genera Dataverse, senza collisioni fra utenti |
| Doppioni | Il wizard potrebbe generare due volte lo stesso ID se due persone salvano insieme; la **chiave alternativa** rifiuta il secondo → si ritenta | Impossibili |

**Scelta di partenza: A**, perché funziona in ogni caso e non dipende dal test. Attenzione: la colonna primaria di una tabella **non si converte** da testo ad Autonumber a tabella creata. Se il test dà esito positivo e si preferisce B, va deciso **prima** di creare `g5_contratto` (test da fare in 5 minuti su una tabella usa-e-getta). Alternativa a basso rischio: provare B, e se l'import dello storico fallisce, ricreare la sola tabella `g5_contratto` quando è ancora vuota.

---

## 4. Dove Dataverse non replica PostgreSQL

| # | Regola in PostgreSQL | Perché Dataverse non la replica | Soluzione scelta | Dove sta il controllo |
|---|---|---|---|---|
| R1 | Indice univoco parziale `ux_contratto_stand_edizione`: un solo contratto **non annullato** per (edizione, stand) | Le chiavi alternative non hanno `WHERE`; una chiave su (edizione, stand) bloccherebbe anche il nuovo contratto su uno stand con contratto annullato | 1) Il wizard calcola gli stand liberi (nessun contratto con `g5_stato <> annullato` per quell'edizione) e non offre gli altri. 2) Controllo finale prima del salvataggio: `CountRows(Filter(...)) = 0`. 3) Flusso Power Automate sulla creazione/modifica che avvisa se trova un doppione (copre due persone che salvano insieme). 4) PostgreSQL rifiuta comunque il doppione al caricamento (rete di sicurezza di BID) | **Wizard** + **flusso** |
| R2 | `CHECK (stato <> 'firmato' OR data_firma IS NOT NULL)` | Dataverse non ha vincoli fra colonne. Una business rule "obbligatorio se firmato" funziona nei moduli, ma **[verificare]** se vale per le app Canvas e per l'API | Nel wizard il pulsante *Firma* non si abilita senza data. Flusso di controllo come R1. Lo stato `firmato` si imposta solo dal wizard | **Wizard** (+ flusso) |
| R3 | `partita_iva ~ '^[0-9]{11}$'` | Il testo non ha controlli di formato | `IsMatch(txtPiva, "^\d{11}$")` (esattamente 11 cifre) nel form dell'espositore; lo script `valida_csv.py` la controlla sullo storico | **Form** espositore + script di import |
| R3b | `anno` come `smallint` | La colonna primaria è testo | Testo di 4 caratteri; il formato `20nn` si controlla nell'app e nello script di import | **Script di import** |
| R4 | `CHECK (data_fine >= data_inizio)` su `edizione` | Nessun vincolo fra colonne | Le edizioni sono 3 e si caricano una volta: controllo nello script di import e a mano per il 2026. Se un giorno si modificano dall'app, va controllato nel form | **Import** (nessun form per ora) |
| R5 | `NOT NULL` | *Business required* è un obbligo dell'interfaccia: **[verificare]** se anche `Patch` e il Dataflow lo rispettano | Il wizard e i form lo controllano con `IsBlank`; lo script di import controlla i campi vuoti; PostgreSQL rifiuta i `NULL` al caricamento | **Wizard**, **form**, **script** |
| R6 | `time` (`ora_apertura`, `ora_chiusura`) | Dataverse non ha il tipo "solo ora" | Testo `HH:MM` | **Import** (formato) |
| R7 | `DEFAULT 0` su `sconto_pct`, `DEFAULT 'firmato'` su `stato` | I default di Dataverse esistono per Choice e Sì/No ma **[verificare]** per i decimali | `sconto_pct` lo imposta sempre il wizard (0 se non c'è sconto). Per `stato` vedi assunzione A3 | **Wizard** |
| R8 | Chiave primaria **composta** (`voce_listino`, `riga_contratto`) | Dataverse usa sempre un GUID | Chiavi alternative composte (§2.5, §2.7): garantiscono l'unicità e permettono l'upsert. Il GUID non deve mai finire in `id_contratto` | **Chiavi alternative** |

Replicabili senza lavoro in più: `partita_iva` e `nome` univoci (chiavi alternative), CHECK sulle liste chiuse (Choice), CHECK numerici (minimo/massimo), `ON DELETE CASCADE` (relazione Parentale), FK (lookup obbligatorie).

Regole che *non sono* nello schema SQL e quindi **non** si impongono (es. `imponibile = imponibile_listino × (1 − sconto_pct)`): lo script di validazione le controlla solo come segnalazione sui dati storici (Fase 3), non diventano vincoli.

---

## 5. Ordine di creazione

Si creano prima le tabelle senza lookup, poi quelle che le puntano; le chiavi alternative per ultime, perché Dataverse le indicizza in modo asincrono e un indice non pronto blocca gli import.

| # | Tabella | Dipende da |
|---|---|---|
| 1 | `g5_edizione` | — |
| 2 | `g5_padiglione` | — |
| 3 | `g5_espositore` | — |
| 4 | `g5_stand` | padiglione, edizione |
| 5 | `g5_voce_listino` | edizione |
| 6 | `g5_contratto` | edizione, espositore, stand |
| 7 | `g5_riga_contratto` | contratto |

Dopo ogni tabella: record di prova, lookup che funziona, record cancellato (Fase 2).
Alla fine: creare le chiavi alternative (stato *Attiva* prima dell'import), poi pubblicare la Solution.

---

## 6. Controllo di copertura (47 colonne di `schema.sql`)

| Tabella | Colonne SQL | In questa specifica |
|---|---|---|
| `edizione` | 5 | 5 (`anno`, `data_inizio`, `data_fine`, `ora_apertura`, `ora_chiusura`) |
| `padiglione` | 2 | 2 (`codice`, `nome`) |
| `stand` | 5 | 5 (`codice_stand`, `padiglione`, `mq`, `posizione`, `attivo_dal`) |
| `espositore` | 7 | 7 |
| `voce_listino` | 7 | 7 |
| `contratto` | 14 | 14 |
| `riga_contratto` | 7 | 7 |
| **Totale** | **47** | **47** (nessuna in più, nessuna in meno) |

Le tabelle `espositore_alias`, `tipo_biglietto`, `biglietto`, `varco`, `passaggio_varco`, `scansione_stand`, `contatto_stand`, `anomalia`, `utente`, `parametro` e le altre dello schema sono di BID e **non** hanno una tabella Dataverse in questa Solution.
