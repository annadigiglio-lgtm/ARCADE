"""Prepara lo zip da condividere con BID (cartella su Google Drive).

Raccoglie in un unico file il LEGGIMI, i CSV per l'import e i documenti aggiornati.
Lo zip va in power-platform/data/consegne/, che è esclusa da Git.
Prima di scrivere controlla che nei file non ci siano indirizzi email: i CSV per BID
non devono contenere referenti o contatti.

Uso (dalla cartella power-platform/consegna-bid):
    python -I prepara_pacchetto.py
Per un nuovo invio: aggiornare LEGGIMI.md e l'elenco FILE qui sotto, poi rilanciare.
"""
import datetime
import os
import re
import sys
import zipfile

QUI = os.path.dirname(os.path.abspath(__file__))
PP = os.path.dirname(QUI)                 # power-platform/
REPO = os.path.dirname(PP)

# (file sorgente relativo alla radice del repository, percorso dentro lo zip)
FILE = [
    ("power-platform/consegna-bid/LEGGIMI.md", "LEGGIMI.md"),
    ("power-platform/data/contratti-C2026-0200.csv", "dati/contratti-C2026-0200.csv"),
    ("power-platform/data/righe-C2026-0200.csv", "dati/righe-C2026-0200.csv"),
    ("power-platform/power-automate/FL-05.md", "documenti/FL-05.md"),
    ("docs/wiki/inventario-dataverse.md", "documenti/inventario-dataverse.md"),
    ("power-platform/app-scansione/README.md", "documenti/app-scansione.md"),
    ("docs/wiki/piano-bad.md", "documenti/piano-bad.md"),
]

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
AMMESSI = {"indirizzo-del-team@example.com"}


def main():
    mancanti = [s for s, _ in FILE if not os.path.exists(os.path.join(REPO, s))]
    if mancanti:
        sys.exit("File mancanti: " + ", ".join(mancanti))
    for sorgente, _ in FILE:
        with open(os.path.join(REPO, sorgente), encoding="utf-8-sig", errors="ignore") as f:
            trovati = {e for e in EMAIL.findall(f.read()) if e not in AMMESSI and "@OData." not in e}
        if trovati:
            sys.exit(f"Indirizzi email in {sorgente}: il pacchetto non viene creato")
    oggi = datetime.date.today().isoformat()
    cartella = os.path.join(PP, "data", "consegne")
    os.makedirs(cartella, exist_ok=True)
    destinazione = os.path.join(cartella, f"ARCADE-BAD-per-BID_{oggi}.zip")
    radice = f"ARCADE-BAD-per-BID_{oggi}/"
    with zipfile.ZipFile(destinazione, "w", zipfile.ZIP_DEFLATED) as z:
        for sorgente, dentro in FILE:
            z.write(os.path.join(REPO, sorgente), radice + dentro)
    print(f"OK: {len(FILE)} file -> {destinazione}")


if __name__ == "__main__":
    main()
