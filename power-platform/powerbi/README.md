# Report Power BI

Responsabili: **Cristian Provenzano** e **Yenje Boum Durand**. Consultati: Anna (viste e accesso al DB), Daniel (stessi numeri nel web).

Il report che la direzione usa per rispondere alle sei domande del brief e leggere i KPI. Qui c'è cosa costruire, da quali dati, in che ordine e come si verifica.

## Regole

- Power BI legge **PostgreSQL su Supabase** (schema `arcade`) con l'utente **`bad_powerbi`**, in sola lettura. Non legge Dataverse ([decisione 0005](../../docs/wiki/decisioni/0005-dataverse-sincronizzato-con-postgresql.md)): così i numeri sono gli stessi del cruscotto e del portale.
- I KPI si leggono dalle viste `v_kpi_*` e **non si ricalcolano in DAX** ([decisione 0003](../../docs/wiki/decisioni/0003-kpi-in-viste-sql.md)). In DAX si fanno solo somme, filtri e formati delle colonne già calcolate. Se manca un numero, si chiede una vista ad Anna.
- **Nessun dato personale** nel report: niente referenti, niente email. La vista `v_contatti_espositore` contiene le email e **non si usa**. I dati sui minori solo aggregati.
- La password di `bad_powerbi` la manda Anna in privato e non si scrive in nessun file. Power BI Desktop non la salva nel `.pbix`.
- Le definizioni dei KPI sono in [kpi.md](../../docs/wiki/kpi.md); i valori di controllo in [dati.md](../../docs/wiki/dati.md#numeri-di-controllo).

## Collegamento

1. Power BI Desktop → Recupera dati → **Database PostgreSQL**.
2. Server: host del *Session pooler* di Supabase (porta 5432), database `postgres`. Parametri da Anna ([guida Supabase](../../docs/wiki/guida-supabase.md)).
3. Modalità **Importa**: i dati storici non cambiano e la modalità DirectQuery sarebbe lenta sulle viste delle presenze, che richiedono circa 6 secondi.
4. Utente `bad_powerbi`, crittografia SSL attiva.
5. Si caricano solo le tabelle e le viste elencate sotto.

## Modello dati

| Tabella o vista | Uso | Relazione |
|---|---|---|
| `edizione` | filtro per anno | `anno` → tutte le tabelle con `edizione` |
| `padiglione` | filtro per padiglione | `codice` → `stand.padiglione` |
| `stand` | mq, posizione | `codice_stand` → `contratto.codice_stand` |
| `contratto` | vendite 2026, stato, incassi | — |
| `riga_contratto` | composizione del ricavo | `id_contratto` → `contratto` |
| `espositore` | **solo** `id_espositore`, `ragione_sociale`, `settore`, `citta` | `id_espositore` → `contratto` |
| `v_kpi_visitatori`, `v_kpi_visitatori_giorno` | visitatori | per edizione e giorno |
| `v_presenze_stimate`, `v_kpi_picco_padiglione`, `v_kpi_picco_fiera` | affluenza e picco | per edizione e padiglione |
| `v_kpi_saturazione` | stand e mq venduti, saturazione | per edizione e padiglione |
| `v_kpi_ricavo_mq` | ricavo e ricavo per mq | per edizione e padiglione |
| `v_kpi_costo_contatto`, `v_kpi_costo_contatto_fiera` | costo per contatto | per stand e per fiera |
| `v_visite_stand_ora` | visite agli stand per ora | per stand |
| Calendario (tabella DAX) | date di vendita e di firma | su `data_firma` |

## Pagine obbligatorie

| ID | Pagina | Risponde a | Contenuto | Fonti | Entro | Chi |
|---|---|---|---|---|---|---|
| **PB-01** | **Sintesi direzione** | KPI richiesti; "come va il 2025 rispetto al 2024?" | schede con visitatori giornalieri, picco, saturazione, ricavo per mq, costo per contatto, imponibile; variazione rispetto all'edizione precedente | viste KPI | 2026-11-17 | Cristian |
| **PB-02** | **Padiglioni e spazi** | "quali padiglioni rendono di più?" | ricavo, saturazione e ricavo per mq per padiglione ed edizione; stand venduti per posizione; P2 sotto il 30% in evidenza | `v_kpi_saturazione`, `v_kpi_ricavo_mq`, `contratto`, `stand` | 2026-11-18 | Cristian |
| **PB-04** | **Vendite 2026 e incassi** | fase "prima"; SAL del 4/12 | contratti 2026 per stato (preventivo, firmato, annullato), imponibile venduto, acconti e saldi incassati, da incassare e in ritardo. **Qui deve comparire C2026-0200** | `contratto`, `riga_contratto`; vista incassi da chiedere | 2026-11-18 | Yenje |
| PB-03 | Espositori e rinnovi | "quali espositori tornano e quali perdiamo?" | tornati, persi e nuovi per edizione; tasso di rinnovo (2025: 79,5%); settori | `contratto`, `espositore`; vista rinnovi da chiedere | 2026-11-19 | Cristian |
| PB-05 | Pubblico e biglietteria | "in quali giorni il pubblico compra?", "quanti biglietti diventano ingressi?" | biglietti per giorno di acquisto e canale, tipi, provenienza, fasce d'età aggregate, conversione da venduti a entrati (96,4%) | viste da chiedere | 2026-11-19 | Yenje |
| PB-06 | Affluenza | "a che ora i padiglioni sono più pieni?" | curva delle presenze stimate per giorno e padiglione, picco con l'ora | `v_presenze_stimate`, `v_kpi_picco_*` | 2026-11-23 | Cristian |
| PB-07 | Stand e contatti | costo per contatto | visite per stand e ora, contatti, costo per contatto per padiglione (mediana), stand senza dati | `v_visite_stand_ora`, `v_kpi_costo_contatto*` | 2026-11-23 | Yenje |

Valori attesi per controllare il report (da [kpi.md](../../docs/wiki/kpi.md)):

| KPI | 2024 | 2025 |
|---|---|---|
| Visitatori giornalieri | 46.425 | 55.498 |
| Picco della fiera | ~13.300 | ~16.100 |
| Saturazione in mq | 66,1% | 70,8% |
| Ricavo per mq | 233 € | 248 € |
| Imponibile contratti | 706.310,35 € | 821.730,60 € |
| Costo per contatto | — | 391 € |

## Viste da chiedere ad Anna

Senza queste, PB-03, PB-04 e PB-05 andrebbero calcolate in DAX, cosa che non facciamo. I nomi sono una proposta: li decide Anna.

| Vista | Contenuto | Serve a |
|---|---|---|
| `v_kpi_rinnovo` | espositori tornati, persi e nuovi per edizione | PB-03 |
| `v_incassi_contratto` | per contratto: acconto e saldo calcolati, pagati sì/no, giorni di ritardo | PB-04 |
| `v_vendite_biglietti_giorno` | biglietti e persone per giorno di acquisto e canale | PB-05 |
| `v_kpi_conversione` | biglietti entrati / venduti per edizione | PB-05 |

## Pagine e funzioni facoltative

Funzioni presenti in Power BI Desktop senza licenze in più. Si usano per mostrare i numeri delle viste, non per ricalcolarli.

| # | Idea | Funzione | Dove |
|---|---|---|---|
| PB-F1 | Previsione delle vendite 2026 | previsione nel riquadro Analisi del grafico a linee | PB-04 |
| PB-F2 | Scomposizione del ricavo | albero di scomposizione: edizione → padiglione → posizione → voce | PB-02 |
| PB-F3 | Cosa influisce sul rinnovo | oggetto visivo "Fattori di influenza chiave" | PB-03 |
| PB-F4 | Scheda espositore | pagina di drill-through senza dati personali | da PB-03 e PB-07 |
| PB-F5 | Picco con permanenze diverse | 90 / 120 / 180 minuti, calcolati nel DB con la tabella `parametro` (da chiedere ad Anna) | PB-06 |
| PB-F6 | Qualità dei dati | anomalie per codice e fonte dalla tabella `anomalia` | nuova pagina |
| PB-F7 | Versione per telefono | layout mobile di PB-01 e PB-04 | PB-01, PB-04 |

## Cosa si consegna

In questa cartella:

- il report salvato come **progetto Power BI** (`ARCADE-direzione.pbip` con le cartelle `.Report` e `.SemanticModel`): sono file di testo, quindi su Git si vede cosa cambia. Si salva con File → Salva con nome → tipo "Progetto di Power BI (.pbip)"; se la voce non c'è, va attivata in Opzioni → Funzionalità in anteprima;
- `verifica-numeri.md`: per ogni pagina, il valore del report, il valore della vista e il valore del web, con la data del controllo. Si fa con Anna e Daniel prima della finale ([analisi](../../docs/wiki/analisi-funzionale.md#8-integrazione-con-bid), S-09).

## Prima di iniziare

- [ ] Parametri di `bad_powerbi` da Anna (S-05)
- [ ] Power BI Desktop aggiornato sul PC di Cristian e Yenje
- [ ] Collegamento di prova: conteggi di `contratto` (198 + contratti 2026 sincronizzati) e `stand` (130)
- [ ] Richiesta ad Anna delle quattro viste mancanti (S-06)
