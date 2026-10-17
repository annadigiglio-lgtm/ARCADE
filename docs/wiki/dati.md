# Dati del cliente

Consegnati al kickoff (2026-10-16), cartella `MATERIALI CLIENTE/ARCADE_Milano_dati/`.
I dati sono sintetici ma costruiti come quelli reali, con le loro imperfezioni. I nomi sono inventati ma vanno trattati come **dati personali**.

Analisi completa svolta il 2026-10-17 su tutti i file.

## File ricevuti

| File | Righe | Formato | Contenuto |
|---|---|---|---|
| `ARCADE_Commerciale.xlsx` | vedi fogli | Excel | Dati commerciali |
| `biglietteria_2024.csv` | 35.719 | `;`, decimali con virgola, date `GG/MM/AAAA hh:mm` | Un biglietto per riga |
| `biglietteria_2025.csv` | 42.556 | come 2024 | Un biglietto per riga |
| `tornelli_2024.csv` | 46.824 | `;`, ora locale, fine riga CRLF | Un passaggio ai varchi per riga |
| `tornelli_2025.csv` | 55.992 | `,`, **UTC** ISO 8601 | Un passaggio ai varchi per riga |
| `visite_stand_2025.csv` | 2.451 | `,` | Scansioni aggregate per stand e per ora |
| `contatti_stand_2025.csv` | 1.707 | `,` | Contatti (lead) raccolti agli stand |

Tutti i file sono in UTF-8.

### Fogli di `ARCADE_Commerciale.xlsx`

| Foglio | Righe | Contenuto |
|---|---|---|
| LEGGIMI | 5 | Descrizione dei fogli |
| Espositori | 135 | Anagrafica aziende (hanno esposto almeno una volta o sono in trattativa) |
| Planimetria | 130 | Stand: padiglione, mq, posizione (linea/angolo/penisola/isola), `attivo_dal` |
| Listino_2026 | 20 | Spazio al mq per padiglione, maggiorazioni, sponsorizzazioni, extra, condizioni |
| Contratti | 198 | 88 del 2024 e 110 del 2025, con acconto, saldo, sconto, rinnovo |
| Righe_contratto | 950 | Dettaglio voci di ogni contratto |

## Cosa sappiamo dei dati

### Commerciale
- I totali coincidono con il brief: **88 contratti / 706.310 €** nel 2024 e **110 / 821.731 €** nel 2025 (`imponibile_eur`).
- Le righe di contratto sono coerenti: quantità × prezzo = importo, somma delle righe = `imponibile_listino_eur`, sconto applicato correttamente, mq dello spazio = mq in planimetria.
- Planimetria: 115 stand (4.580 mq) nel 2024 e 130 stand (4.677 mq) dal 2025 (15 nuovi stand piccoli in P3).
- Prezzi dello spazio al mq: 2024 P1 165, P2 150, P3 110; 2025 P1 180, P2 160, P3 120; listino 2026 P1 190, P2 170, P3 125.
- Le maggiorazioni (angolo +10%, penisola +15%, isola +25%) sono sempre presenti dove servono.
- Sponsorizzazioni vendute: rispettano la disponibilità del listino in entrambe le edizioni.
- Rinnovi (dopo l'abbinamento di A16-A17): **70 espositori del 2024 tornano nel 2025, 18 persi, 40 nuovi**. Coincide con il flag `rinnovo` dei contratti 2025.
- 10 espositori in anagrafica non hanno contratti: sono "in trattativa".
- Condizioni: acconto del 30% alla firma (scadenza = firma + 15 giorni), saldo entro 30 giorni prima dell'apertura, prelazione sullo stesso stand fino al 31 marzo.

### Biglietteria
- Nessun biglietto duplicato, nessuna riga duplicata, nessun acquisto dopo il giorno di validità.
- Vendite concentrate a ridosso della fiera: circa il 60% a dicembre. Le vendite alla cassa sono quasi tutte nel giorno stesso.
- Canali: Online ~70%, Cassa ~20%, Rivenditore partner ~10%.
- Sconto: solo `EARLY10` riduce il prezzo (-10%); `SCUOLA` e `STUDENTI` sono registrati ma **non cambiano il prezzo**.
- I biglietti Family valgono 4 persone (`Persone = 4`); tutti gli altri 1.
- Il Business (Day) è usato solo il venerdì mattina, coerente con il nome.

### Tornelli
- 4 varchi: P1 Nord, P1 Sud, P2 Ovest, P3 Est. **Registrano solo gli ingressi, non le uscite.**
- Orari dei passaggi: 09:00-17:30 ora locale in entrambe le edizioni (2025 dopo la conversione da UTC, +1 ora).
- Nessun ingresso valido in un giorno diverso da quello del biglietto.
- Un biglietto può passare più volte (fino a 7): rientri e spostamenti tra padiglioni.
- Biglietti venduti e mai usati: 1.272 (2024), 1.515 (2025).

### Stand (solo 2025)
- Visite e contatti esistono per 84 stand su 110 venduti: 26 stand non hanno dati (P1 10, P2 5, P3 11).
- I contatti sono sempre associati all'espositore giusto (coerenti con i contratti).
- Le visite seguono l'orario 09:00-18:00, con picco tra le 12 e le 13.

## Anomalie trovate

Ogni anomalia ha una gestione proposta. Lo stato diventa `decisa` quando il team la approva (e, se serve, il cliente).

| # | File | Anomalia | Quanti | Gestione proposta | Stato |
|---|---|---|---|---|---|
| A1 | tornelli | Formato diverso tra 2024 e 2025: colonne, separatore, nomi | tutti | Unica tabella `passaggio_varco` con caricamento distinto per anno | proposta |
| A2 | tornelli | 2024 in ora locale, 2025 in UTC | tutti | Salvare come `timestamptz`, 2024 interpretato come `Europe/Rome` | proposta |
| A3 | tornelli | Nomi varchi diversi (`P1 Nord` / `P1-Nord`) | tutti | Tabella di decodifica varchi → codice unico | proposta |
| A4 | tornelli | Esito diverso (`1`/`0` contro `OK`/`KO`) | tutti | Campo booleano `esito_ok` | proposta |
| A5 | tornelli | Passaggi con codice biglietto inesistente (es. `T24955068`), tutti respinti | 35 + 35 | Si caricano con flag `CODICE_SCONOSCIUTO` ma non si contano | proposta |
| A6 | tornelli | Passaggi respinti (KO) con codice valido | 195 + 221 | Si caricano, non si contano come ingressi | proposta |
| A7 | tornelli | **Doppie letture**: passaggio valido con il passaggio valido precedente dello stesso biglietto allo stesso varco meno di 2 minuti prima | 972 + 1.195 | Flag `DOPPIA_LETTURA`, escluse dal conteggio | proposta |
| A8 | biglietteria | Decimali con virgola, date `GG/MM/AAAA` | tutti | Conversione nel caricamento | proposta |
| A9 | biglietteria | Tipi biglietto rinominati tra 2024 e 2025 (`Intero` → `Giornaliero intero`, `Abb. 3gg` → `Abbonamento 3 giorni`, ecc.) | 8 tipi | Tabella di decodifica → tipo unico | proposta |
| A10 | biglietteria | **Provincia scritta in 3 modi**: sigla, maiuscolo, minuscolo (`MI`, `MILANO`, `Milano`) | 64 valori per 21 province | Tabella di decodifica → sigla | proposta |
| A11 | biglietteria | Provincia vuota | 4.683 | `NULL` = "non indicata" | proposta |
| A12 | biglietteria | Fascia d'età vuota | 3.101 | `NULL` = "non indicata" | proposta |
| A13 | biglietteria | Fascia `famiglia` usata come età per i biglietti Family (e 200 Family senza fascia) | 5.121 | Non è un'età: trattarla come "non applicabile" | proposta |
| A14 | biglietteria | Codici `SCUOLA` e `STUDENTI` senza effetto sul prezzo, anche su omaggi e stampa | 13.746 | Tenere il codice, segnalarlo al cliente | da chiedere |
| A15 | biglietteria | Fasce d'età non allineate al tipo (`Ridotto 8-14 anni` contro fasce `8-13` e `14-17`) | — | Solo segnalazione | proposta |
| A16 | Contratti | **Tutti i contratti 2024 senza `id_espositore` e `partita_iva`** | 88 | Abbinamento per ragione sociale: 33 identici, 46 dopo normalizzazione (maiuscole, `srl` / `S.r.l.`, forma societaria mancante), 9 con la regola di A17. Abbinamento salvato in una tabella di decodifica | proposta |
| A17 | Contratti | Contratti 2024 con nome storpiato: la forma `S.r.l.s.` è diventata una "s." attaccata all'ultima parola (`Bussola Gears.` = `Bussola Gear S.r.l.s.`, `Dora Techs.` = `Dora Tech S.r.l.s.`) | 9 | Regola di normalizzazione specifica: abbinamento univoco per tutti e 9 | proposta |
| A18 | Contratti | `rinnovo = vero` su 6 contratti 2025 il cui espositore sembrava assente nel 2024 | 6 | Risolta da A17: sono espositori con il nome storpiato. Dopo l'abbinamento il flag `rinnovo` è coerente al 100% | risolta |
| A19 | Contratti | Scadenza acconto **dopo** scadenza saldo (C2025-0120) | 1 | Segnalare, non correggere | proposta |
| A20 | Contratti | Saldo pagato senza acconto (C2024-0006, C2025-0093, -0095, -0141, -0157, -0171, -0189, -0197) | 8 | Considerare l'acconto incluso nel saldo, da confermare | da chiedere |
| A21 | Contratti | Saldo pagato prima dell'acconto (C2024-0078, C2025-0116) | 2 | Segnalare | proposta |
| A22 | Contratti | Saldo mai pagato (C2024-0019, -0027, -0085, C2025-0099, -0102, -0108, -0144, -0169) | 8 | Crediti aperti: sono dati, non errori | proposta |
| A23 | Contratti | **Saldo pagato dopo la fiera** (2025-01-19 e 2026-01-18) | 11 + 14 | Sono dati, non errori: utili per i solleciti | proposta |
| A24 | Contratti | Acconti in ritardo rispetto alla scadenza | 53 + 68 | Sono dati, non errori: utili per i solleciti | proposta |
| A25 | Righe | Una maggiorazione con prezzo decimale (C2024-0073, 445,5) | 1 | Accettabile (10% di un importo dispari) | proposta |
| A26 | visite_stand | **Valore anomalo**: P1-A02, 2025-12-19 ore 08:00, 912 scansioni (prima dell'apertura, 8 volte il totale del giorno) | 1 | Esclusa dai conteggi con flag `FUORI_SCALA` | proposta |
| A27 | visite_stand | Ore mancanti per alcuni stand (27-29 righe invece di 30) | 43 stand | Ora mancante = 0 scansioni (da confermare) | da chiedere |
| A28 | contatti | **Minori** (14-17) con consenso marketing `SI` | 14 | Il consenso di un minore non vale da solo: email non visibili all'espositore | da chiedere |
| A29 | contatti | Consenso marketing vuoto | 9 | Vuoto = nessun consenso: email non visibili | proposta |
| A30 | contatti | Stessa email su più stand | 19 email | Normale (stessa persona, stand diversi) | proposta |
| A31 | biglietteria | **Minori come titolari** del biglietto (fasce 0-7, 8-13, 14-17) con provincia | ~28.000 | Solo dati aggregati, mai a livello di singolo biglietto nelle interfacce | proposta |

> Nota: nel primo esame si era segnalata una "codifica errata" del simbolo `m²` nel listino. Era un problema di visualizzazione del terminale, non dei dati: il file è corretto.

## Numeri di controllo

Servono per verificare che il caricamento nel DB sia giusto: dopo il caricamento le query devono dare questi valori.

| Controllo | 2024 | 2025 |
|---|---|---|
| Biglietti | 35.719 | 42.556 |
| Persone sui biglietti (Family = 4) | 42.979 | 51.259 |
| Ordini | 21.500 | 25.500 |
| Passaggi ai varchi (tutti) | 46.824 | 55.992 |
| Passaggi validi (OK, codice noto) | 46.594 | 55.736 |
| Passaggi validi senza doppie letture | 45.622 | 54.541 |
| Biglietti distinti entrati | 34.447 | 41.041 |
| Visitatori giornalieri (persone × biglietto-giorno) | 46.425 | 55.498 |
| Visitatori unici (persone × biglietto) | 41.434 | 49.441 |
| Contratti | 88 | 110 |
| Imponibile contratti | 706.310,35 € | 821.730,60 € |
| Mq venduti | 3.028 | 3.313 |
| Contatti agli stand | — | 1.707 |
| Visite agli stand (senza A26) | — | 35.301 |
