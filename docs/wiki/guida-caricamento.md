# Guida: caricamento dei dati storici

Carica nel database i dati 2024-2025 del cliente, applicando la pulizia descritta in [dati.md](dati.md). Script in [`db/caricamento/`](../../db/caricamento/).

## Requisiti (una volta sola)

- **PostgreSQL** installato sul PC (serve il programma `psql`; non serve che il server locale sia acceso).
- **Python** con la libreria per l'Excel: `pip install openpyxl`.
- I **file del cliente** nella cartella `MATERIALI CLIENTE/ARCADE_Milano_dati`, accanto alla cartella `ARCADE`. Se sono altrove, si indica il percorso (vedi sotto).
- Il file **`.env`** nella cartella `ARCADE`: copiare `.env.example` in `.env` e compilarlo con host, utente `bid_app.<PROJECT-REF>` e password (vedi [guida-supabase.md](guida-supabase.md)). Il file `.env` è escluso da Git.

## Avvio

Dal terminale, nella cartella `ARCADE`:

```powershell
.\db\caricamento\carica.ps1
```

oppure, se i dati sono in un'altra cartella:

```powershell
.\db\caricamento\carica.ps1 -Dati "C:\percorso\ARCADE_Milano_dati"
```

Dura qualche minuto. Alla fine stampa la **tabella di verifica**: ogni riga deve avere esito `OK`.

## Cosa fa

| Passo | File | Cosa fa |
|---|---|---|
| 1 | `excel_in_csv.py` | Converte i fogli dell'Excel commerciale in CSV (cartella `excel_csv` accanto ai dati), senza modificarli |
| 2 | `00_staging.sql` | Crea tabelle **temporanee** con colonne di solo testo |
| 3 | `01_copia.sql` | Copia i file così come sono nelle tabelle temporanee |
| 4 | `02_trasforma.sql` | **Pulizia e caricamento** nelle tabelle vere, registrando ogni anomalia nella tabella `anomalia` |
| 5 | `03_verifica.sql` | Confronta i dati caricati con i numeri di controllo di [dati.md](dati.md) |

- Il passo 4 è **una sola transazione**: se qualcosa fallisce, il database resta com'era.
- Si può **rieseguire** quante volte serve: ogni volta cancella e ricarica i dati commerciali e di affluenza (non tocca edizioni, varchi, province, tipi di biglietto, parametri, utenti).
- Quando arriveranno i contratti 2026 dalla sincronizzazione con Dataverse, il passo 4 andrà limitato allo storico per non cancellarli.

## Dove sta ogni regola di pulizia

Nel file `02_trasforma.sql`, cercando il codice dell'anomalia (es. `A17`):

| Anomalia | Regola |
|---|---|
| A1-A4 | Tornelli 2024 e 2025 caricati con due query diverse nella stessa tabella; 2024 in ora italiana, 2025 da UTC; varchi e esiti tradotti |
| A5 | Codice biglietto inesistente → flag `CODICE_SCONOSCIUTO` |
| A7 | Doppia lettura (stesso biglietto, stesso varco, entro 120 secondi) → flag `DOPPIA_LETTURA` |
| A8 | Decimali con virgola convertiti |
| A9 | Tipo di biglietto tradotto con `tipo_biglietto_alias` |
| A10-A11 | Provincia tradotta in sigla con `provincia_alias`; vuota = NULL |
| A12-A13 | Fascia d'età vuota o `famiglia` = NULL |
| A16-A17 | Contratti 2024 abbinati all'espositore per ragione sociale (esatta, normalizzata, regola "s." finale) |
| A26 | Scansioni prima dell'apertura → flag `FUORI_SCALA` |
| A28-A29 | Consenso vuoto = no; l'email di minori non è visibile agli espositori (vista `v_contatti_espositore`) |

## Primo caricamento

Eseguito il 2026-10-23 sul database condiviso Supabase: **28 controlli su 28 OK**, nessun contratto non abbinato.
