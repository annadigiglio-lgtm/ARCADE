# KPI

Le definizioni operative **non sono fornite dal cliente**: le proponiamo noi, le concordiamo con BAD, le fa approvare il cliente.
Ogni KPI è calcolato **in un solo posto**, una vista SQL in [`db/viste_kpi.sql`](../../db/viste_kpi.sql), usata sia dalle API BID sia da Power BI. Vedi [decisione 0003](decisioni/0003-kpi-in-viste-sql.md).

Stato possibile: `proposto` → `concordato con BAD` → `approvato dal cliente`.

I valori riportati sotto sono calcolati sui dati del cliente (2026-10-17), prima del caricamento nel DB. Dopo il caricamento le viste devono dare gli stessi numeri.

---

## 1. Visitatori

- **Domanda:** quante persone sono venute alla fiera?
- **Problema:** i tornelli contano le *letture*, non le persone. Un biglietto Family fa entrare 4 persone con una lettura; chi passa da un padiglione all'altro viene letto più volte; un abbonato entra in più giorni.
- **Proposta: tre misure, ognuna con un significato chiaro**

| Misura | Definizione | 2024 | 2025 |
|---|---|---|---|
| **Ingressi ai padiglioni** | Passaggi validi ai varchi (esito OK, biglietto esistente, senza doppie letture) | 45.622 | 54.541 |
| **Visitatori giornalieri** (KPI principale) | Per ogni giorno, persone dei biglietti entrati almeno una volta (Family = 4) | 46.425 | 55.498 |
| **Visitatori unici** | Persone dei biglietti entrati almeno una volta in tutta la fiera | 41.434 | 49.441 |

- **Confronto con il brief:** le "presenze" del brief (45.700 e 54.600) corrispondono quasi esattamente agli **ingressi ai padiglioni**. Probabilmente il cliente conta le letture ai varchi: va chiesto (domanda D2).
- **Vista:** `v_kpi_visitatori`, `v_kpi_visitatori_giorno`
- **Dove si vede:** cruscotto staff (in diretta), Power BI (confronto tra edizioni)
- **Stato:** proposto

## 2. Picco di presenza nei padiglioni

- **Domanda:** quante persone c'erano al massimo in ogni padiglione, e a che ora?
- **Problema:** i varchi registrano **solo gli ingressi**. Senza le uscite le presenze vanno stimate.
- **Proposta di modello:**
  - una persona è dentro un padiglione dal suo passaggio fino al passaggio successivo della stessa giornata (se va in un altro padiglione, passa di là);
  - dopo l'ultimo passaggio della giornata resta per un tempo di **permanenza** (parametro, proposta 120 minuti), senza superare la chiusura (19:00);
  - le presenze si calcolano ogni 5 minuti; il picco è il valore massimo.
- **Valori stimati con permanenza 120 minuti** (picco del giorno più affollato, il sabato):

| | Fiera | P1 | P2 | P3 |
|---|---|---|---|---|
| 2024 (sab 21/12) | ~13.300 alle 11:55 | ~9.300 | ~2.700 | ~1.300 |
| 2025 (sab 20/12) | ~16.100 alle 11:55 | ~11.300 | ~3.200 | ~1.600 |

- **Sensibilità:** il picco dipende molto dalla permanenza scelta. Con 90 minuti il picco 2025 è ~13.800, con 180 minuti ~19.100. Va scelta con il cliente (domanda D3) e dichiarata come assunzione.
- **Conferma indiretta:** le visite agli stand hanno il massimo tra le 12 e le 13, quindi le persone entrate tra le 10 e le 11 restano in fiera per qualche ora.
- **Vista:** `v_presenze_stimate`, `v_kpi_picco_padiglione`, `v_kpi_picco_fiera`
- **Dove si vede:** cruscotto staff (curva in diretta), Power BI
- **Stato:** proposto

## 3. Saturazione degli spazi espositivi

- **Domanda:** quanta parte dello spazio disponibile abbiamo venduto?
- **Definizione:** mq venduti (contratti firmati) / mq disponibili nell'edizione (stand con `attivo_dal` ≤ edizione). Si riporta anche il rapporto in numero di stand.

| | Totale mq | P1 | P2 | P3 | Stand venduti |
|---|---|---|---|---|---|
| 2024 | **66,1%** (3.028 / 4.580) | 95,5% | **22,4%** | 100% | 88 / 115 |
| 2025 | **70,8%** (3.313 / 4.677) | 98,5% | **28,6%** | 100% | 110 / 130 |

- **Da segnalare al cliente:** P1 e P3 sono pieni, **P2 (Esports & Community) è venduto per meno di un terzo**. È la risposta più chiara alla domanda "quali padiglioni rendono di più".
- **Vista:** `v_kpi_saturazione`
- **Stato:** proposto

## 4. Ricavo per metro quadrato

- **Domanda:** quanto rende ogni mq venduto, per padiglione?
- **Definizione proposta:** imponibile netto dei contratti (spazio, maggiorazioni, extra, sponsorizzazioni, dopo lo sconto) / mq venduti.

| | Totale | P1 | P2 | P3 |
|---|---|---|---|---|
| 2024 | **233 €/mq** (706.310 € / 3.028 mq) | 236 | 235 | 210 |
| 2025 | **248 €/mq** (821.731 € / 3.313 mq) | 258 | 221 | 227 |

- **Varianti da discutere** (domanda D5):
  - solo spazio e maggiorazioni (senza extra e sponsor): misura il prezzo reale dello spazio;
  - ricavo / mq **disponibili** (2025: 176 €/mq): misura quanto rende il padiglione intero, includendo lo spazio invenduto.
- **Vista:** `v_kpi_ricavo_mq`
- **Stato:** proposto

## 5. Costo per contatto

- **Domanda:** quanto paga un espositore per ogni contatto raccolto al suo stand?
- **Definizione proposta:** imponibile del contratto dell'espositore / numero di contatti raccolti allo stand. A livello di fiera: somma degli imponibili / somma dei contatti, solo per gli stand che hanno raccolto contatti.
- **Valori 2025** (84 stand con contatti su 110; solo il 2025 ha dati agli stand):
  - fiera: **391 € per contatto** (mediana tra gli stand 363 €, da 110 € a 1.938 €)
  - per padiglione (mediana): P1 395 €, P2 537 €, P3 301 €
  - in alternativa sulle visite (scansioni): 18,9 € per visita
- **Da decidere** (domanda D4): contatti o visite? Imponibile intero o solo la parte dello spazio?
- **Vista:** `v_kpi_costo_contatto`, `v_kpi_costo_contatto_fiera`
- **Dove si vede:** portale espositori (solo il proprio valore), Power BI
- **Stato:** proposto

---

## Altri indicatori utili (dalle domande del brief)

| Domanda del brief | Indicatore | Primo dato |
|---|---|---|
| Quali padiglioni rendono di più? | Ricavo, saturazione e ricavo/mq per padiglione | P1 genera ~74% del ricavo 2025 |
| Quali espositori tornano e quali perdiamo? | Tasso di rinnovo | 70 su 88 tornati nel 2025 (79,5%), 18 persi, 40 nuovi |
| In quali giorni il pubblico compra i biglietti? | Vendite per giorno e canale | ~62% dei biglietti venduti a dicembre |
| A che ora i padiglioni sono più pieni? | Curva delle presenze stimate | Picco tra le 11:30 e le 12:00 |
| Quanti biglietti venduti diventano ingressi? | Biglietti entrati / venduti | 96,4% (2024), 96,4% (2025) |
| Come va il 2025 rispetto al 2024? | Confronto di tutti i KPI | Visitatori giornalieri +19,5%, ricavi +16,3% |
