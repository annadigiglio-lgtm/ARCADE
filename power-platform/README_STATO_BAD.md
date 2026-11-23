# Power Platform (BAD)

Cartella del team BAD. Lo stato completo è nella wiki: [`docs/wiki/power-platform.md`](../docs/wiki/power-platform.md).
Il formato di scambio con BID è in [`README.md`](README.md) (scritto da BID).

## Cartelle

| Cartella | Contenuto |
|---|---|
| `solution-build/` | Soluzione ARCADE BAD esportata (`ARCADEBAD_1_0_0_4.zip`, non gestita): si importa da make.powerapps.com → Soluzioni → Importa |
| `solution/ARCADEBAD/` | La stessa soluzione scompattata con `pac solution unpack`: tabelle, chiavi, relazioni, app |
| `canvas-src/` | App back-office: `genera_schermate.py` (da qui nascono tutte le schermate), sorgenti `.pa.yaml`, ultima versione `FUSIONWORK-BACKOFFICE_v13.msapp` |
| `solution-src/` | Script della soluzione: `genera_solution.py`, `patch_export.py`, `genera_scansione.py` (soluzione separata con la tabella `g5_scansione_stand`), `inventario.py` (genera `docs/wiki/inventario-dataverse.md`) |
| `import-scripts/` | `prepara_import.py`: dai dati puliti di BID prepara i file di import e il report di validazione. Non scrive in Dataverse |
| `power-automate/` | Flussi Power Automate (Adam) |
| `powerbi/` | Report Power BI (Cristian, Yenje) |
| `app-scansione/` | App di scansione allo stand (Alessandro, Lorenzo) |
| `data/` | CSV con dati personali dei referenti: **esclusa da Git**, non si condivide |

## Rigenerare l'app

Istruzioni in [`docs/wiki/guida-app-backoffice.md`](../docs/wiki/guida-app-backoffice.md). In breve:

```powershell
cd power-platform/canvas-src
python -I genera_schermate.py
pac canvas pack --sources backoffice_src --msapp FUSIONWORK-BACKOFFICE_vN.msapp --layout SourceCode
```

## Esportare la soluzione aggiornata

```powershell
pac auth create --environment https://orgbd2a22ed.crm4.dynamics.com
pac solution export --name ARCADEBAD --path solution-build/ARCADEBAD_x_y_z_w.zip --managed false
pac solution unpack --zipfile solution-build/ARCADEBAD_x_y_z_w.zip --folder solution/ARCADEBAD --packagetype Unmanaged --processCanvasApps
```

Poi, dalla cartella `solution-src/`, `python -I inventario.py ../solution-build/ARCADEBAD_x_y_z_w.zip` per aggiornare l'inventario.
