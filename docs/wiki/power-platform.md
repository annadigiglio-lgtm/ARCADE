# Power Platform (BAD)

Stato della parte BAD: ambiente, soluzione, dati, app, flussi e report. Aggiornato al 2026-11-16. Prossimo SAL: 2026-12-04 ([piano](piano-bad.md)).

## In breve

| Elemento | Stato |
|---|---|
| Ambiente `ARCADE-Milano-BAD-G5` (Developer) | attivo |
| Soluzione **ARCADE BAD** (`ARCADEBAD`, editore Gruppo5BAD, prefisso `g5`) 1.0.0.4 | esportata in `power-platform/solution-build/` |
| 7 tabelle Dataverse, uguali alle tabelle commerciali di [`schema.sql`](../../db/schema.sql) | fatte, dati caricati e verificati |
| App back-office *FUSIONWORK-BACKOFFICE Commerciale* (9 schermate) | fatta, aperta in Studio senza errori |
| App di scansione allo stand | da fare ([analisi](../../power-platform/app-scansione/README.md)) |
| Flussi Power Automate | da fare ([elenco](../../power-platform/power-automate/README.md)) |
| Report Power BI | da fare ([pagine](../../power-platform/powerbi/README.md)) |
| Sincronizzazione Dataverse → PostgreSQL | da concordare con Anna ([decisione 0005](decisioni/0005-dataverse-sincronizzato-con-postgresql.md)) |

## Tabelle e dati

Le tabelle hanno gli stessi nomi di `schema.sql` con il prefisso `g5_` (es. `g5_voce_listino`). Specifica in [schema-dataverse.md](schema-dataverse.md), inventario della soluzione esportata in [inventario-dataverse.md](inventario-dataverse.md), corrispondenza con PostgreSQL in [mappatura-dataverse.md](mappatura-dataverse.md).

Lo storico è quello pulito da BID su Supabase: l'abbiamo importato e validato, non ripulito.

| Tabella | Supabase | Dataverse |
|---|---|---|
| edizione | 3 | 3 |
| padiglione | 3 | 3 |
| espositore | 135 | 135 |
| stand | 130 | 130 |
| voce_listino | 20 | 20 |
| contratto | 198 | 201 (198 + 3 contratti 2026 di prova) |
| riga_contratto | 950 | 974 (950 + 24 righe di prova) |

Totali di controllo uguali a Supabase: importo righe 1.604.733,50 €, imponibile 1.528.040,95 €, mq 4.677.

Contratti 2026 creati dall'app durante le prove:

| Contratto | Stato | Note |
|---|---|---|
| C2026-0199 | annullato | prova di annullamento |
| C2026-0200 | firmato | stand P1-A03, 10.838 €, acconto e saldo pagati: è il contratto da portare in PostgreSQL per il SAL del 4/12 |
| C2026-0201 | preventivo | stand P1-A01, 17.440 € |

Come sono stati caricati: edizione, padiglione ed espositore con *Importa dati da Excel* del portale; stand, listino, contratti e righe con la Web API di Dataverse, in upsert sulla chiave alternativa (ripetere il caricamento aggiorna, non duplica). Le date delle edizioni importate da Excel erano indietro di un giorno e sono state corrette il 2026-11-04 ([decisione 0010](decisioni/0010-niente-import-excel-per-le-date.md)).

## App back-office

Nove schermate, solo dati Dataverse:

| Schermata | Cosa fa |
|---|---|
| Panoramica | indicatori dell'edizione, ultimi contratti, occupazione per padiglione |
| Stand | stand per padiglione, libero o venduto (si ricava dai contratti non annullati) |
| Espositori | elenco, ricerca, scheda, nuovo espositore |
| Contratti | elenco, righe, Firma, Annulla, Segna pagato, sollecito |
| Nuovo contratto | procedura in 4 passi: espositore, stand libero, servizi dal listino, sconto e riepilogo |
| Scadenze e incassi | acconti e saldi per urgenza, Segna pagato, sollecito |
| Rinnovi e prelazione | espositori dell'edizione precedente con il loro stand, "Prepara preventivo" |
| Listino | voci per categoria, modifica di prezzo e disponibilità |
| Controlli dati | 8 controlli sulle regole (stand venduto una volta, firmato con data, partita IVA, totali) |

Come si genera e si apre l'app: [guida-app-backoffice.md](guida-app-backoffice.md).

## Regole di business verificate sui 198 contratti

- Prezzo area = mq × prezzo al mq del padiglione (2026: P1 190, P2 170, P3 125 €/mq).
- Maggiorazione sull'area: angolo +10%, penisola +15%, isola +25%.
- Imponibile = listino × (1 − sconto); sconti 0, 5, 10, 15 o 20%.
- Acconto 30% con scadenza firma + 15 giorni; saldo 70% entro 30 giorni prima della fiera (2026: 18/11).
- Numero contratto `C<anno>-<nnnn>`, progressivo su tutte le edizioni.
- Rinnovo = espositore presente nell'edizione precedente.

## Documenti BAD

- [Analisi funzionale](analisi-funzionale.md): requisiti, ruoli, processi, architettura, piano
- [Assunzioni BAD](assunzioni-bad.md): cosa abbiamo dovuto supporre e va confermato
- [Guida ambiente Power Platform](guida-ambiente-power-platform.md): utenti, ruoli, condivisione, export della soluzione
- [Idee di miglioramento](idee-miglioramento.md): cosa aggiungere se avanza tempo
- [Gantt del progetto](../piano/gantt-arcade.html) (da aprire nel browser)

## Punti aperti

- [ ] Sincronizzazione verso PostgreSQL: export CSV (opzione B) per il SAL del 4/12: importatore di BID pronto, mancano i CSV con i record
- [ ] Utenti BID nell'ambiente: l'aggiunta del 2026-11-04 si è fermata con l'errore "Graph throttling"
- [ ] Ambiente Developer non gestito: sospeso dal 2026-12-15, quindi la soluzione va esportata nel repository
- [ ] Tabelle `cre10_*` create all'inizio dal piano automatico di Power Apps, rimaste nell'ambiente fuori dalla soluzione: eliminarle è da decidere
- [ ] Assunzioni A1–A15 da confermare con Anna
