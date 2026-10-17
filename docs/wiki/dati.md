# Dati del cliente

Consegnati al kickoff (2026-10-16), cartella `MATERIALI CLIENTE/ARCADE_Milano_dati/`.
I dati sono sintetici ma costruiti come quelli reali, con le loro imperfezioni. I nomi sono inventati ma vanno trattati come **dati personali**.

## File ricevuti

| File | Righe (circa) | Separatore | Contenuto |
|---|---|---|---|
| `ARCADE_Commerciale.xlsx` | vedi fogli | — | Dati commerciali (fogli sotto) |
| `biglietteria_2024.csv` | 35.700 | `;` | Un biglietto per riga |
| `biglietteria_2025.csv` | 42.500 | `;` | Un biglietto per riga |
| `tornelli_2024.csv` | 46.800 | `;` | Un passaggio ai varchi per riga |
| `tornelli_2025.csv` | 56.000 | `,` | Un passaggio ai varchi per riga |
| `visite_stand_2025.csv` | 2.450 | `,` | Scansioni per stand per ora |
| `contatti_stand_2025.csv` | 1.700 | `,` | Contatti (lead) raccolti agli stand |

### Fogli di `ARCADE_Commerciale.xlsx`

| Foglio | Righe | Contenuto |
|---|---|---|
| LEGGIMI | — | Descrizione dei fogli |
| Espositori | 135 | Anagrafica aziende (esposto almeno una volta o in trattativa) |
| Planimetria | 130 | Stand per padiglione, mq, posizione, `attivo_dal` (prima edizione in cui esiste) |
| Listino_2026 | 20 | Voci di listino 2026 (spazio al mq per padiglione, extra) |
| Contratti | 198 | Contratti 2024 e 2025 con acconto, saldo, sconto, rinnovo |
| Righe_contratto | 950 | Dettaglio voci di ogni contratto |

## Colonne principali

**Biglietteria:** `ID ordine; ID biglietto; Data acquisto; Canale; Tipo biglietto; Giorno valido; Prezzo; Persone; Fascia eta titolare; Provincia; Codice sconto`

**Tornelli 2024:** `data; ora; varco; codice; esito`
**Tornelli 2025:** `timestamp_utc, ticket_code, gate_id, result`

**Visite stand:** `codice_stand, data, ora, scansioni`

**Contatti stand:** `id_contatto, codice_stand, id_espositore, timestamp, email, fascia_eta, provincia, consenso_marketing, interesse`

## Anomalie trovate

Prime osservazioni, da approfondire con l'analisi completa. Ogni anomalia va registrata qui con **come la gestiamo** e, se serve, una decisione in [decisioni/](decisioni/README.md).

| # | File | Anomalia | Gestione |
|---|---|---|---|
| A1 | tornelli | Formato diverso tra 2024 e 2025 (colonne, nomi, separatore) | _da decidere_: normalizzare in un'unica tabella |
| A2 | tornelli | 2024 in ora locale (`data`+`ora`), 2025 in UTC (`timestamp_utc`) | _da decidere_: convertire tutto in un fuso unico |
| A3 | tornelli | Nomi varchi diversi (`P1 Nord` contro `P1-Nord`) | _da decidere_: tabella di decodifica varchi |
| A4 | tornelli | Esito codificato diversamente (`1` contro `OK`) | _da decidere_: mappare su un unico valore |
| A5 | biglietteria | Decimali con virgola (`55,00`) e date `GG/MM/AAAA` | Conversione in fase di caricamento |
| A6 | biglietteria | Tipi biglietto diversi tra 2024 e 2025 (es. `Intero` contro `Giornaliero intero`) | _da decidere_: tabella di decodifica tipi |
| A7 | biglietteria | Biglietti multi-persona (`Family`, `Persone` = 4) e abbonamenti `3 giorni` | Impatta il conteggio visitatori: vedi [kpi.md](kpi.md) |
| A8 | biglietteria | Campi vuoti (fascia d'età, provincia) su alcune righe | _da decidere_ |
| A9 | Contratti | `id_espositore` e `partita_iva` mancanti su alcune righe | _da decidere_: abbinamento per ragione sociale |
| A10 | Contratti | Ragione sociale scritta in modo diverso (es. punto finale, forma societaria) | _da decidere_: normalizzazione nomi |
| A11 | Listino | Codifica caratteri errata (`m²` letto come `m�`) | Leggere con la codifica corretta |
| A12 | contatti | Email e fascia d'età, possibili minori | Tutela dati: vedi [architettura.md](architettura.md) |

## Da verificare nell'analisi

- [ ] Duplicati (stesso biglietto, stesso passaggio ripetuto)
- [ ] Ingressi con codice biglietto inesistente in biglietteria
- [ ] Ingressi fuori dagli orari o dai giorni della fiera
- [ ] Biglietti usati in un giorno diverso da quello valido
- [ ] Stand nei contratti che non esistono in planimetria (o non attivi in quell'edizione)
- [ ] Stand venduti due volte nella stessa edizione
- [ ] Importi: `imponibile_eur` coerente con listino e sconto? Somma righe = totale contratto?
- [ ] Date di pagamento prima della firma o mancanti
- [ ] Totali confrontati con i numeri del brief (biglietti, presenze, ricavi)
- [ ] Varchi: ci sono uscite o solo ingressi? Serve per calcolare le presenze in un dato momento
