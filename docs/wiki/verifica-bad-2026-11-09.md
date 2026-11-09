# Verifica della consegna BAD — 2026-11-09

## Esito e perimetro

La consegna `ARCADE-BAD_2026-11-06`, nella cartella accanto al repository,
è coerente con l'architettura BID/BAD e con il modello commerciale PostgreSQL.
Non dimostra ancora un'integrazione funzionante: mancano l'export commerciale
con record, il caricamento verso PostgreSQL e il confronto con Power BI.
Prima del SAL 2 del 13/11 servono le verifiche sotto.

Revisione statica di documenti, SQL e sorgenti Canvas esportati. Nessun accesso
live a Dataverse, Supabase o Render; nessuna modifica ai dati o alla consegna BAD.
I conteggi dei record nell'ambiente e le prove in Studio restano dichiarazioni
BAD, non una nuova certificazione del 9/11. Le precedenti modifiche locali
del repository sono state conservate.

## Materiali riscontrati

| Materiale | Riscontro locale |
|---|---|
| Solution `ARCADEBAD_1_0_0_4.zip` | Archivio ZIP integro, versione XML 1.0.0.4, una Canvas app inclusa |
| Solution scompattata | 7 tabelle commerciali `g5_` |
| App esportata | 9 schermate `scr*.pa.yaml` in `canvas-src/app_esportata_1_0_0_4/Src/` |
| Contratti e righe di scambio | Entrambi i CSV hanno solo intestazione: **0 record** |
| Power BI | Nessun `.pbix` nel pacchetto; presente il README di pianificazione |
| Power Automate e scansione | Dichiarati da realizzare nel README BAD |

Il README BAD del 4/11 dichiara 198 contratti storici e 950 righe, più 3 contratti
2026 di prova e 24 righe (201/974). C2026-0200 è firmato e pagato secondo BAD;
C2026-0199 è annullato e C2026-0201 è preventivo. Non sono incassi reali.

## Cosa è allineato

- Le 7 entità corrispondono a `edizione`, `padiglione`, `espositore`, `stand`,
  `voce_listino`, `contratto`, `riga_contratto` di [schema.sql](../../db/schema.sql).
- La mappatura BAD usa i codici di business per le FK, mai i GUID dentro le
  chiavi SQL; `C2026-0200` rientra nei 12 caratteri di `id_contratto`.
- `sconto_pct` è una frazione (0.10 = 10%); stati e vincolo di firma coincidono
  con il formato di scambio BID. Anno testuale e ora `HH:MM` richiedono conversione.
- Dataverse alimenta PostgreSQL in una direzione; API e Power BI devono leggere
  le stesse viste KPI. La proposta BAD di export CSV per SAL 2 coincide con
  l'opzione B già proposta in [architettura](architettura.md).
- Il divieto di due contratti non annullati per stand/edizione coincide con
  l'indice SQL: anche un preventivo occupa lo stand ai fini della disponibilità.

La compatibilità tecnica delle conversioni non equivale ad approvazione delle
assunzioni di processo o del cliente.

## Problemi e azioni

I percorsi BAD sotto sono relativi alla radice della consegna separata.

### P1 — Integrazione SAL 2 ancora da dimostrare (BID + BAD)

I CSV sono vuoti e l'importatore commerciale BID non è implementato.
La mappatura esiste in `docs/bad/mappatura-dataverse-postgres.md`, ma cita
ancora l'inventario 1.0.0.2: va confrontata con l'export effettivo 1.0.0.4.
La lettura API deve risolvere lookup e valori Choice nei codici/etichette attesi:
non basta rimuovere il prefisso `g5_`.

Richiedere export reale di C2026-0200 e relative righe, con anagrafiche necessarie;
validare FK, date, decimali e importi, poi importare in una transazione con upsert
idempotente. Ripetere l'import deve lasciare invariati conteggi e totali.
Se l'export è uno snapshot completo, gestire anche le righe eliminate, altrimenti
un semplice upsert lascerà righe obsolete. Tenere esplicita la natura di prova.

### P1 — “Venduto” ha significati diversi (BAD + BID)

In `scrHome.pa.yaml:782` il testo “venduti” conta `StatoTxt <> "annullato"`:
include i preventivi. In `db/viste_kpi.sql:126` la saturazione usa solo `firmato`.
Il preventivo C2026-0201 può quindi produrre differenze anche a sincronizzazione
riuscita. Distinguere **occupato/prenotato** (non annullati) e **venduto**
(firmati); mantenere i KPI ufficiali coerenti con le viste SQL.

### P1 — Salvataggio parziale e concorrenza (BAD)

In `scrNuovo.pa.yaml:1742–1751` il numero nasce da `Max(colContratti, ...) + 1`,
il controllo stand è su una collezione aggiornata nel client e testata e righe
sono scritte con `Patch` separati. Non si vede un rollback delle scritture già
riuscite in caso di errore successivo. Due sessioni possono scegliere lo stesso
numero o lo stesso stand; una chiave univoca sul numero non protegge la coppia
stand/edizione. In `scrEspositori.pa.yaml:674` anche l'ID espositore è calcolato
nel client dal codice maggiore.

Provare due sessioni e un errore durante la creazione delle righe. Prevedere
assegnazione sicura dei codici, controllo server della prenotazione e recupero
del salvataggio parziale. PostgreSQL blocca le collisioni al caricamento, ma
non impedisce che si creino prima in Dataverse.

### P2 — Collezioni e limite fisso delle righe (BAD)

`App.pa.yaml:30` carica i contratti in `colContratti`; controlli, numerazione e
indicatori lavorano poi su quella copia. Il README segnala già limiti di lettura:
non assumere che tutti i record siano caricati quando il volume cresce.
In `scrContratti.pa.yaml:17` e `scrControlli.pa.yaml:16` si usa `Sequence(16)`
per caricare le righe: qualsiasi riga numero 17 o maggiore resta fuori dai
dettagli e dalla verifica dei totali. Lo schema SQL non impone un massimo di 16.
Eliminare il limite implicito o concordare e far rispettare un limite esplicito;
verificare completezza delle letture oltre i limiti configurati nell'app.

### P2 — Modifica listino senza edizione (BAD)

`scrListino.pa.yaml:710` seleziona il record con `LookUp('Voci listino', Codice =
ls_galListino.Selected.Codice)`. La chiave SQL e la mappatura sono invece
**(edizione, codice)**. Con lo stesso codice in più edizioni il record cercato
è ambiguo. Usare il record/GUID selezionato o entrambe le componenti della chiave;
provare due edizioni con identico codice prima di estendere il listino.

### P2 — Provenienza dello storico e assunzioni (team / cliente)

Gli 88 abbinamenti espositore dei contratti 2024 restano proposte BID
(anomalie A16/A17), anche se copiati in Dataverse: non considerarli confermati
per rinnovi e confronti. L'indice rinnovo 0–3 è una proposta BAD, non un KPI
approvato dal cliente. Nel registro `assunzioni-bad.md` A13 identifica sia
l'ambiente Developer sia l'indice rinnovo; A14 compare due volte. Assegnare ID
univoci senza confondere questi codici con le anomalie dei dati BID.

La correzione delle date di un giorno è dichiarata risolta da BAD: controllare
nell'export 2026 il 18–20/12 e il saldo di C2026-0200 al 18/11. Le affermazioni
del pacchetto su licenze, permessi e sospensione Developer sono da verificare
con tutor e documentazione vigente prima di usarle per pianificare il servizio;
questa revisione locale non le convalida.

### P2 — Scansioni e report incompleti (BAD + BID)

Non risultano ancora consegnati app scansione, tabella Dataverse relativa,
flussi Power Automate e report Power BI. Concordare GUID/chiave stabile della
scansione per evitare doppioni a ogni import: il solo `bigserial` PostgreSQL
non riconosce una scansione già ricevuta. Definire timestamp con fuso,
stand, edizione, `quantita = 1`, `origine = 'app'` e autorizzazioni per stand.

## Criterio di chiusura prima del SAL 2

Nota sulla documentazione BID: i collegamenti già presenti in indice e TODO
a `docs/presentazioni/stato-2026-11-06/README.md` non si risolvono nella copia
locale controllata. Ripristinare i materiali della presentazione o correggere
i percorsi prima di condividerli; non sono stati ricreati durante questa verifica.

1. BAD consegna export con record e mappatura aggiornata; BID e BAD confermano B.
2. BID valida e importa il contratto di prova e tutte le righe, senza duplicati
   alla ripetizione e senza lasciare dati parziali in caso di errore.
3. BAD distingue prenotati/firmati e il team confronta importi e KPI fra app,
   PostgreSQL, web e Power BI, dichiarando quando manca ancora un report.
4. BAD prova concorrenza e fallimenti di salvataggio; il team registra gli esiti.

Fonti locali principali: `power-platform/README_STATO_BAD.md`,
`docs/bad/condivisione-bid.md`, `docs/bad/mappatura-dataverse-postgres.md`,
`docs/bad/assunzioni-bad.md` e i sorgenti esportati della 1.0.0.4.
