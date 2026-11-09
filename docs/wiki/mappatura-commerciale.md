# Mappatura commerciale BAD → PostgreSQL

Copia di lavoro acquisita il **2026-11-09** da
`ARCADE-BAD_2026-11-06/docs/bad/mappatura-dataverse-postgres.md`.
Il testo BAD sotto cita la 1.0.0.2: il pacchetto ricevuto è la **1.0.0.4**,
quindi i nomi effettivi e i valori esportati vanno verificati sull’export reale.
Le conversioni sono tecnicamente compatibili con lo schema BID; non costituiscono
approvazione automatica delle assunzioni del cliente.

Per contratto e righe, lo [script](../../db/caricamento/importa_commerciale.py)
accetta il formato normalizzato descritto in [Power Platform](../../power-platform/README.md),
non un CSV grezzo del portale con intestazioni localizzate, GUID o Choice numeriche.
I lookup devono diventare codici di business e lo sconto una frazione.
Le anagrafiche non vengono importate dallo script e devono già esistere.

Prossimo SAL: **4 dicembre 2026**. Stato e criticità nella
[verifica BAD](verifica-bad-2026-11-09.md).

---

## Specifica ricevuta da BAD

Aggiornato 3 novembre 2026. Direzione unica: **Dataverse → PostgreSQL** (decisione 0005).
Fonti: `db/schema.sql` (PostgreSQL) e `docs/bad/stato-dataverse.md` (inventario della Solution ARCADE BAD 1.0.0.2).

## Regola generale

| Tema | Dataverse | PostgreSQL | Conversione alla sincronizzazione |
|---|---|---|---|
| Nome tabella | `g5_<nome SQL>` (es. `g5_voce_listino`) | `arcade.<nome SQL>` | togliere `g5_` |
| Nome colonna | `g5_<nome SQL>` | `<nome SQL>` | togliere `g5_` |
| Chiave | GUID di sistema `g5_<tabella>id` + chiave alternativa sui codici | chiave primaria sui codici | **il GUID non si copia**: si usano i codici |
| Lookup | riferimento al GUID; nell'export compare il **valore della colonna primaria** (il codice) | colonna FK con il codice | valore primario = codice (es. `P1`, `2026`, `ESP001`, `C2025-0089`) |
| Scelta | etichetta identica al valore SQL (`linea`, `firmato`…) | `text` con CHECK | etichetta così com'è |
| Sì/No | `Sì`/`No` (true/false via API) | `boolean` | true/false |
| Data | *Solo data* | `date` | AAAA-MM-GG, nessun fuso |
| Decimale | punto decimale nell'API | `numeric` | nessuna |
| Colonne di sistema | `createdon`, `modifiedon`, `ownerid`, `statecode`… | — | non si copiano |

## Tabelle e colonne

| Dataverse | PostgreSQL | Differenza / conversione |
|---|---|---|
| **`g5_edizione`** | **`edizione`** | |
| `g5_anno` (testo 4, primaria) | `anno smallint` PK | testo → numero (A2) |
| `g5_data_inizio`, `g5_data_fine` | `data_inizio`, `data_fine date` | — |
| `g5_ora_apertura`, `g5_ora_chiusura` (testo `HH:MM`) | `ora_apertura`, `ora_chiusura time` | testo → time (A1) |
| **`g5_padiglione`** | **`padiglione`** | |
| `g5_codice`, `g5_nome` | `codice`, `nome` | — |
| **`g5_espositore`** | **`espositore`** | |
| `g5_id_espositore`, `g5_ragione_sociale`, `g5_partita_iva`, `g5_settore`, `g5_citta`, `g5_referente`, `g5_email_referente` | stesse colonne | `partita_iva` resta testo (zeri iniziali) |
| **`g5_stand`** | **`stand`** | |
| `g5_codice_stand`, `g5_mq`, `g5_posizione` | `codice_stand`, `mq`, `posizione` | — |
| `g5_padiglione` (lookup) | `padiglione varchar(2)` FK | codice del padiglione |
| `g5_attivo_dal` (lookup → edizione) | `attivo_dal smallint` FK | anno → numero |
| **`g5_voce_listino`** | **`voce_listino`** | PK composta (edizione, codice) = chiave alternativa composta |
| `g5_edizione` (lookup) | `edizione smallint` | anno → numero |
| `g5_codice`, `g5_descrizione`, `g5_unita`, `g5_prezzo_unitario`, `g5_disponibilita`, `g5_note` | stesse colonne | `disponibilita` vuota = illimitata (non 0) |
| **`g5_contratto`** | **`contratto`** | |
| `g5_id_contratto` | `id_contratto` | codice commerciale `C<anno>-<nnnn>`, mai il GUID |
| `g5_edizione`, `g5_espositore`, `g5_stand` (lookup) | `edizione`, `id_espositore`, `codice_stand` | codici |
| `g5_stato` (scelta) | `stato text` | etichetta |
| `g5_data_firma`, `g5_acconto_*`, `g5_saldo_*` | stesse colonne `date` | — |
| `g5_imponibile_listino`, `g5_sconto_pct`, `g5_imponibile` | stesse colonne | `sconto_pct` è una frazione (0.10 = 10%) |
| `g5_rinnovo` (Sì/No) | `rinnovo boolean` | — |
| **`g5_riga_contratto`** | **`riga_contratto`** | PK composta (id_contratto, riga) = chiave alternativa composta |
| `g5_contratto` (lookup, eliminazione a cascata) | `id_contratto` FK `ON DELETE CASCADE` | codice del contratto |
| `g5_riga`, `g5_codice_voce`, `g5_descrizione`, `g5_quantita`, `g5_prezzo_unitario`, `g5_importo` | stesse colonne | `codice_voce` **non** è una lookup sul listino |

## Regole che Dataverse non impone (controlli altrove)

| # | Regola SQL | Dove si controlla |
|---|---|---|
| R1 | un solo contratto non annullato per (edizione, stand) – indice parziale | app (stand liberi) + PostgreSQL al caricamento |
| R2 | `firmato` ⇒ `data_firma` | app (pulsante Firma) + PostgreSQL |
| R3 | partita IVA di 11 cifre | form espositore + `prepara_import.py` |
| R4 | `data_fine >= data_inizio` | `prepara_import.py` |

## Differenze con lo stato precedente dell'ambiente

- Le tabelle `cre10_*` create da Plans **non** fanno parte della Solution ARCADE BAD e non vanno sincronizzate. Se esistono ancora nell'ambiente, la loro eliminazione va decisa con il team (operazione distruttiva).
- `cre10_vocelistino` (senza underscore) è sostituita da `g5_voce_listino`.
- `cre10_visitastand` non ha corrispondenza nelle tabelle commerciali: fuori scopo.
- Tabelle di PostgreSQL senza tabella Dataverse (di BID): `espositore_alias`, biglietteria, varchi, scansioni, contatti, `anomalia`, `utente`, `parametro`.
