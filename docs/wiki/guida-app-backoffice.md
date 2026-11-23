# Guida app back-office

Come si genera, si apre e si corregge l'app *FUSIONWORK-BACKOFFICE Commerciale*. Perché la scriviamo da codice: [decisione 0009](decisioni/0009-app-scritta-da-codice.md).

## Come è fatta

- Un solo file sorgente: `power-platform/canvas-src/genera_schermate.py`. Scrive le schermate in `backoffice_src/Src/*.pa.yaml`.
- Nomi delle schermate: `scrHome`, `scrStand`, `scrEspositori`, `scrContratti`, `scrNuovo`, `scrScadenze`, `scrRinnovi`, `scrListino`, `scrControlli`. Il prefisso `scr` serve perché `Stand` ed `Espositori` sono già i nomi delle origini dati.
- Colori e caratteri sono in `App.Formulas` (nomi `nf…`).
- `App.OnStart` carica due collezioni piatte, `colContratti` e `colStand`, con i codici già estratti dalle lookup.
- **Non si modificano le schermate a mano in Studio**: alla generazione successiva le modifiche si perdono.

## Generare e aprire una nuova versione

1. Modificare `genera_schermate.py`.
2. Generare e impacchettare:

```powershell
cd power-platform/canvas-src
python -I genera_schermate.py
pac canvas pack --sources backoffice_src --msapp FUSIONWORK-BACKOFFICE_vN.msapp --layout SourceCode
```

3. In make.powerapps.com aprire l'app in Studio → File → Apri → Sfoglia → il nuovo `.msapp`.
4. Eseguire App → OnStart, poi l'anteprima (F5). In modalità modifica i controlli non rispondono ai clic.
5. Salvare: File → Salva con nome → Questo computer. Gli errori trovati da Studio sono nel file `AppCheckerResult.sarif` dentro il `.msapp` (è uno zip); si leggono `runs[].results[]` e si ignorano le note `acc-*` (accessibilità).
6. Quando la versione è buona: Salva e Pubblica, poi esportare la soluzione ([guida ambiente](guida-ambiente-power-platform.md#esportare-la-soluzione)).

## Numero del contratto e ID espositore

Dal 2026-11-23 li assegna Dataverse, non l'app: le colonne `g5_id_contratto` e `g5_id_espositore` hanno la numerazione automatica (richiesta della [verifica di BID](verifica-bad-2026-11-09.md)). Prima il telefono calcolava "massimo + 1" sulla copia locale dei contratti: due salvataggi insieme potevano avere lo stesso numero, e un contratto di prova `C2026-9999` ha prodotto `C2026-10000`.

| Colonna | Formato | Primo numero |
|---|---|---|
| `g5_id_contratto` | `C2026-{SEQNUM:4}` | C2026-0202 |
| `g5_id_espositore` | `ESP{SEQNUM:3}` | ESP136 |

- Nell'app i nuovi record si salvano **senza** questi campi; il numero si legge dal record restituito da `Patch` (`gblNuovo.'ID contratto'`).
- Le due colonne non sono più obbligatorie lato app (il valore c'è sempre, lo mette il server): se fossero obbligatorie, l'app rifiuterebbe il salvataggio prima di inviarlo.
- **Quando si apriranno le vendite 2027** il formato del contratto va cambiato in `C2027-{SEQNUM:4}` e il valore di partenza riportato a 1 (Web API: modifica della colonna e azione `SetAutoNumberSeed`). Finché il formato dice 2026, l'app non deve creare contratti di un'altra edizione: l'importatore di BID controlla che l'anno del codice sia quello dell'edizione.
- Se il salvataggio delle righe fallisce dopo la creazione del contratto, l'app annulla il contratto appena creato e chiede di riprovare.

## Errori già incontrati e come si risolvono

| Errore | Soluzione |
|---|---|
| Galleria `BrowseLayout_Flexible_SocialFeed_ver5.0` senza `WrapCount` | per le griglie usare `BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0` |
| Nome di colonna non riconosciuto in `AddColumns` | nell'app sono attivi i nomi di colonna come identificatori: i nomi nuovi vanno senza virgolette |
| Colonna `Stato` ambigua in Contratti | c'è anche `statecode` di sistema: si scrive `'Stato (g5_stato)'`; in scrittura `'Stato (Contratti)'.firmato` |
| `ErrBadType` con `IfError` dentro `If` | i due rami devono avere lo stesso tipo: chiudere il ramo con `; true` |
| `ErrIncompatibleTypesForEquality` | le lookup non si confrontano come record: confrontare l'identificativo |
| `ErrInvalidName` con `As a` | con un alias ogni campo va qualificato (`a.StatoTxt`) |
| "Average non può essere utilizzata con una tabella vuota" | controllare prima che la tabella non sia vuota (edizione 2026 senza contratti) |
| Righe dei contratti mancanti | il filtro sulle righe non è delegabile e si ferma a 500 righe: le righe si caricano a blocchi per numero di riga (`CARICA_RIGHE`) |
| Errore di YAML (PA2108, proprietà sconosciuta) | blocca l'apertura del file; gli errori di formula invece no |

Avvisi che restano e non sono errori: `WrnCountRowsMayReturnCachedValue`, `CollectDelegatableDataSource`, `CollectingReadOnlyTable`, `ForAllWithMutation`.

## Regole per le prove

- **Non provare le scritture sui contratti storici**: annullarli o segnarli pagati cambia i 198 dati verificati.
- Per provare si crea un contratto 2026 da Nuovo contratto e poi lo si annulla. I contratti non si cancellano mai.
- Dopo una prova si controllano i conteggi (3, 3, 135, 130, 20 e contratti storici invariati).
