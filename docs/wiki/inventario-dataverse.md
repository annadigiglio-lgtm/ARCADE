# Stato Dataverse – Solution ARCADE BAD

Generato da `power-platform/solution-src/inventario.py` su `ARCADEBAD_1_0_0_7.zip` (versione 1.0.0.7, editore Gruppo5BAD, prefisso `g5`). Sola lettura.

Colonne di sistema (`createdon`, `ownerid`, `statecode`, GUID `g5_<tabella>id`…) escluse: non fanno parte di `schema.sql`.

## `g5_contratto` – Contratto

Proprietà: OrgOwned; change tracking: sì; entity set Web API: `g5_contratti`.

| Colonna | Nome | Tipo | Obbl. | Dettaglio |
|---|---|---|---|---|
| `g5_acconto_pagato_il` | Acconto pagato il | Data | No | Solo data |
| `g5_acconto_scadenza` | Scadenza acconto | Data | No | Solo data |
| `g5_data_firma` | Data firma | Data | No | Solo data |
| `g5_edizione` | Edizione | Lookup | Sì |  |
| `g5_espositore` | Espositore | Lookup | Sì |  |
| `g5_id_contratto` **(primaria)** | ID contratto | Testo | Sì | max 12 |
| `g5_imponibile` | Imponibile | Decimale | Sì | precisione 2, min 0, max 9999999999.99 |
| `g5_imponibile_listino` | Imponibile a listino | Decimale | Sì | precisione 2, min 0, max 9999999999.99 |
| `g5_rinnovo` | Rinnovo | Sì/No | Sì | Sì, No |
| `g5_saldo_pagato_il` | Saldo pagato il | Data | No | Solo data |
| `g5_saldo_scadenza` | Scadenza saldo | Data | No | Solo data |
| `g5_sconto_pct` | Sconto | Decimale | Sì | precisione 4, min 0, max 1 |
| `g5_stand` | Stand | Lookup | Sì |  |
| `g5_stato` | Stato | Scelta | Sì | preventivo, firmato, annullato |

Chiavi alternative: `g5_key_contratto_id` = (g5_id_contratto)

Relazioni N:1: `g5_edizione` → `g5_edizione` (eliminazione: Restrict); `g5_espositore` → `g5_espositore` (eliminazione: Restrict); `g5_stand` → `g5_stand` (eliminazione: Restrict)

## `g5_edizione` – Edizione

Proprietà: OrgOwned; change tracking: sì; entity set Web API: `g5_edizioni`.

| Colonna | Nome | Tipo | Obbl. | Dettaglio |
|---|---|---|---|---|
| `g5_anno` **(primaria)** | Anno | Testo | Sì | max 4 |
| `g5_data_fine` | Data fine | Data | Sì | Solo data |
| `g5_data_inizio` | Data inizio | Data | Sì | Solo data |
| `g5_ora_apertura` | Ora apertura | Testo | Sì | max 5 |
| `g5_ora_chiusura` | Ora chiusura | Testo | Sì | max 5 |

Chiavi alternative: `g5_key_edizione_anno` = (g5_anno)

Relazioni N:1: nessuna

## `g5_espositore` – Espositore

Proprietà: OrgOwned; change tracking: sì; entity set Web API: `g5_espositori`.

| Colonna | Nome | Tipo | Obbl. | Dettaglio |
|---|---|---|---|---|
| `g5_citta` | Città | Testo | No | max 100 |
| `g5_email_referente` | Email referente | Testo | No | max 200 (email) |
| `g5_id_espositore` **(primaria)** | ID espositore | Testo | Sì | max 10 |
| `g5_partita_iva` | Partita IVA | Testo | Sì | max 11 |
| `g5_ragione_sociale` | Ragione sociale | Testo | Sì | max 200 |
| `g5_referente` | Referente | Testo | No | max 200 |
| `g5_settore` | Settore | Testo | No | max 100 |

Chiavi alternative: `g5_key_espositore_id` = (g5_id_espositore); `g5_key_espositore_piva` = (g5_partita_iva)

Relazioni N:1: nessuna

## `g5_padiglione` – Padiglione

Proprietà: OrgOwned; change tracking: sì; entity set Web API: `g5_padiglioni`.

| Colonna | Nome | Tipo | Obbl. | Dettaglio |
|---|---|---|---|---|
| `g5_codice` **(primaria)** | Codice | Testo | Sì | max 2 |
| `g5_nome` | Nome | Testo | Sì | max 100 |

Chiavi alternative: `g5_key_padiglione_codice` = (g5_codice); `g5_key_padiglione_nome` = (g5_nome)

Relazioni N:1: nessuna

## `g5_riga_contratto` – Riga contratto

Proprietà: OrgOwned; change tracking: sì; entity set Web API: `g5_righe_contratto`.

| Colonna | Nome | Tipo | Obbl. | Dettaglio |
|---|---|---|---|---|
| `g5_codice_voce` | Codice voce | Testo | Sì | max 20 |
| `g5_contratto` | Contratto | Lookup | Sì |  |
| `g5_descrizione` **(primaria)** | Descrizione | Testo | Sì | max 500 |
| `g5_importo` | Importo | Decimale | Sì | precisione 2, min -100000000000, max 100000000000 |
| `g5_prezzo_unitario` | Prezzo unitario | Decimale | Sì | precisione 2, min -100000000000, max 100000000000 |
| `g5_quantita` | Quantità | Decimale | Sì | precisione 2, min 0.01, max 99999999.99 |
| `g5_riga` | Riga | Numero intero | Sì | min 1, max 32767 |

Chiavi alternative: `g5_key_riga_contratto` = (g5_contratto, g5_riga)

Relazioni N:1: `g5_contratto` → `g5_contratto` (eliminazione: Cascade)

## `g5_scansione_stand` – Scansione stand

Proprietà: UserOwned; change tracking: sì; entity set Web API: `g5_scansione_stands`.

| Colonna | Nome | Tipo | Obbl. | Dettaglio |
|---|---|---|---|---|
| `g5_edizione` | Edizione | Lookup | Sì |  |
| `g5_id_scansione` **(primaria)** | ID scansione | Testo | Sì | max 36 |
| `g5_origine` | Origine | Testo | Sì | max 20 |
| `g5_quantita` | Quantità | Numero intero | Sì | min 0, max 1000 |
| `g5_rilevato_il` | Rilevato il | Data | Sì | Data e ora, ora locale utente (salvata in UTC) |
| `g5_stand` | Stand | Lookup | Sì |  |

Chiavi alternative: `g5_key_scansione_stand` = (g5_id_scansione)

Relazioni N:1: `g5_edizione` → `g5_edizione` (eliminazione: Restrict); `g5_stand` → `g5_stand` (eliminazione: Restrict)

## `g5_stand` – Stand

Proprietà: OrgOwned; change tracking: sì; entity set Web API: `g5_stands`.

| Colonna | Nome | Tipo | Obbl. | Dettaglio |
|---|---|---|---|---|
| `g5_attivo_dal` | Attivo dal | Lookup | Sì |  |
| `g5_codice_stand` **(primaria)** | Codice stand | Testo | Sì | max 10 |
| `g5_mq` | Metri quadri | Decimale | Sì | precisione 1, min 0.1, max 99999.9 |
| `g5_padiglione` | Padiglione | Lookup | Sì |  |
| `g5_posizione` | Posizione | Scelta | Sì | linea, angolo, penisola, isola |

Chiavi alternative: `g5_key_stand_codice` = (g5_codice_stand)

Relazioni N:1: `g5_attivo_dal` → `g5_edizione` (eliminazione: Restrict); `g5_padiglione` → `g5_padiglione` (eliminazione: Restrict)

## `g5_voce_listino` – Voce listino

Proprietà: OrgOwned; change tracking: sì; entity set Web API: `g5_voci_listino`.

| Colonna | Nome | Tipo | Obbl. | Dettaglio |
|---|---|---|---|---|
| `g5_codice` **(primaria)** | Codice | Testo | Sì | max 20 |
| `g5_descrizione` | Descrizione | Testo | Sì | max 500 |
| `g5_disponibilita` | Disponibilità | Numero intero | No | min -2147483648, max 2147483647 |
| `g5_edizione` | Edizione | Lookup | Sì |  |
| `g5_note` | Note | Testo multiriga | No | max 1000 |
| `g5_prezzo_unitario` | Prezzo unitario | Decimale | No | precisione 2, min -100000000000, max 100000000000 |
| `g5_unita` | Unità | Testo | No | max 50 |

Chiavi alternative: `g5_key_voce_listino` = (g5_codice, g5_edizione)

Relazioni N:1: `g5_edizione` → `g5_edizione` (eliminazione: Restrict)

## Flussi cloud

| Flusso | Stato | Avvio | Connettori |
|---|---|---|---|
| ARCADE – FL-00 – Demo conferma contratto (istantaneo) | attivo | manuale (pulsante) | Dataverse, Office 365 Outlook |
| ARCADE – FL-01 – Promemoria e solleciti di pagamento | attivo | ricorrenza ogni giorno alle 8:00 | Dataverse, Office 365 Outlook |
| ARCADE – FL-02 – Conferma firma | attivo | riga di `g5_contratto` modificata | Dataverse, Office 365 Outlook |
| ARCADE – FL-03 – Invio preventivo PDF | attivo | dall'app (Power Apps V2) | Dataverse, OneDrive for Business, Office 365 Outlook |
| ARCADE – FL-04 – Controllo stand venduto due volte | attivo | riga di `g5_contratto` creata o modificata | Dataverse, Office 365 Outlook |
| ARCADE – FL-05 – Export dati commerciali per PostgreSQL | attivo | ricorrenza ogni 6 ore | Dataverse, OneDrive for Business, Office 365 Outlook |
| ARCADE – FL-06 – Invito al rinnovo e prelazione | attivo | dall'app (Power Apps V2) | Dataverse, Office 365 Outlook |
| ARCADE – FL-07 – Avviso disponibilità esaurita | attivo | riga di `g5_riga_contratto` creata | Dataverse, Office 365 Outlook |
| ARCADE – FL-08 – Riepilogo settimanale | attivo | ricorrenza ogni settimana (lunedì) alle 8:00 | Dataverse, Office 365 Outlook |

## Riferimenti di connessione

| Nome | Connettore | Usato da |
|---|---|---|
| `g5_dataverse_flussi` | Dataverse | FL-00, FL-01, FL-02, FL-03, FL-04, FL-05, FL-06, FL-07, FL-08 |
| `g5_office365_arcade` | Office 365 Outlook | FL-00, FL-01, FL-02, FL-03, FL-04, FL-05, FL-06, FL-07, FL-08 |
| `g5_onedriveforbusiness_arcade` | OneDrive for Business | FL-03, FL-05 |
| `g5_sharedcommondataserviceforapps_5809c` | Dataverse | nessun flusso |
| `g5_sharedcommondataserviceforapps_cfa98` | Dataverse | nessun flusso |
| `g5_sharedoffice365_40869` | Office 365 Outlook | nessun flusso |
| `g5_sharedoffice365_eef66` | Office 365 Outlook | nessun flusso |

## Variabili d'ambiente

I valori non si riportano qui: contengono indirizzi email del team.

| Nome | Tipo | Valore predefinito | Valore corrente nell'export |
|---|---|---|---|
| `g5_CartellaExport` | Testo | sì | no |
| `g5_EmailCommerciale` | Testo | sì | sì |
| `g5_GiorniPreavviso` | Numero | sì | no |
| `g5_ModalitaProva` | Sì/No | sì | no |
| `g5_g5_EmailProva` | Testo | sì | sì |

Totale: 8 tabelle, 53 colonne custom, 10 chiavi, 9 relazioni, 9 flussi.
