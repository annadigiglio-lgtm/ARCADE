# Pacchetto BAD per BID

Aggiornato al 2026-11-23. Referente BAD: Alessandro Terlingo. Lo stesso contenuto è nella [pull request n. 1](https://github.com/annadigiglio-lgtm/ARCADE/pull/1); questo pacchetto raccoglie solo quello che serve per l'integrazione con PostgreSQL.

## Cosa c'è

| File | A cosa serve |
|---|---|
| `dati/contratti-C2026-0200.csv` | contratto C2026-0200 (firmato, stand P1-A03, imponibile 10838.00) nel formato concordato |
| `dati/righe-C2026-0200.csv` | le sue 4 righe (somma 10838.00 = imponibile a listino) |
| `documenti/FL-05.md` | il flusso che esporta i dati commerciali da Dataverse ogni 6 ore |
| `documenti/inventario-dataverse.md` | tabelle, colonne, chiavi e flussi della soluzione ARCADE BAD 1.0.0.7 |
| `documenti/app-scansione.md` | l'app di scansione allo stand; al §5.1 la tabella Dataverse delle scansioni rispetto a `scansione_stand` |
| `documenti/piano-bad.md` | piano BAD fino al SAL del 2026-12-04 |

I CSV non contengono dati personali: l'espositore è indicato solo con il codice (`ESP057`).

## Cosa vi chiediamo

1. Importare C2026-0200:

   ```powershell
   python db/caricamento/importa_commerciale.py --contratti dati/contratti-C2026-0200.csv --righe dati/righe-C2026-0200.csv --applica
   ```

   I file sono già validati senza `--applica` (`Validazione CSV OK: 1 contratti, 4 righe`).
2. Rilanciare lo stesso comando una seconda volta: non deve creare duplicati.
3. Dirci se C2026-0200 compare nel web e nelle viste `v_incassi_contratto`, `v_kpi_saturazione`, `v_kpi_ricavo_mq`.
4. Mandarci in privato la password di `bad_powerbi`, per il primo aggiornamento del report Power BI.

## Cosa è cambiato da parte nostra

| Data | Cambiamento | Effetto per BID |
|---|---|---|
| 2026-11-23 | annullati in Dataverse i contratti di prova C2026-9996…9999 e C2026-10000 | nessuno stand ha due contratti non annullati nella stessa edizione; se arrivano negli export, arrivano come `annullato` |
| 2026-11-23 | FL-05 esporta solo contratti e righe dalle edizioni 2026 in poi | l'importatore non trova più lo storico 2024–2025 |
| 2026-11-23 | ricreata la tabella `g5_scansione_stand` con chiave su `g5_id_scansione` (testo di 36 caratteri, un GUID generato dall'app) | è la colonna `g5_id_scansione uuid` di `scansione_stand`; il CSV delle scansioni seguirà il formato di `import-scansioni.md` |

## Prossimi invii

- export completo da FL-05 (8 file CSV) dopo la prova di import di C2026-0200;
- `scansione_stand.csv` quando l'app di scansione sarà pronta.
