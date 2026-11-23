"""Toglie gli indirizzi email dalle variabili d'ambiente della soluzione scompattata.

Il repository è pubblico: gli indirizzi veri restano solo nell'ambiente (valore corrente).
Da eseguire dopo ogni `pac solution unpack`, prima del commit.
  - valore predefinito con un indirizzo email -> indirizzo-del-team@example.com
  - file environmentvariablevalues.json con un indirizzo email -> eliminato

Uso (dalla cartella power-platform/solution-src):
    python -I segnaposto_email.py ../solution/ARCADEBAD
"""
import os
import re
import sys

SEGNAPOSTO = "indirizzo-del-team@example.com"
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def main(cartella):
    base = os.path.join(cartella, "environmentvariabledefinitions")
    cambiati = 0
    for var in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        defin = os.path.join(base, var, "environmentvariabledefinition.xml")
        with open(defin, encoding="utf-8-sig") as f:
            testo = f.read()
        nuovo = re.sub(r"<defaultvalue>([^<]*)</defaultvalue>",
                       lambda m: f"<defaultvalue>{SEGNAPOSTO}</defaultvalue>"
                       if EMAIL.search(m.group(1)) and m.group(1) != SEGNAPOSTO else m.group(0), testo)
        if nuovo != testo:
            with open(defin, "w", encoding="utf-8", newline="") as f:
                f.write(nuovo)
            cambiati += 1
            print(f"{var}: valore predefinito sostituito")
        valori = os.path.join(base, var, "environmentvariablevalues.json")
        if os.path.exists(valori):
            with open(valori, encoding="utf-8-sig") as f:
                contiene_email = bool(EMAIL.search(f.read()))
            if contiene_email:  # il file va chiuso prima di eliminarlo (Windows)
                os.remove(valori)
                cambiati += 1
                print(f"{var}: valore corrente eliminato")
    # controllo finale: nessun indirizzo, a parte il segnaposto, in tutta la soluzione scompattata
    for radice, _, files in os.walk(cartella):
        for nome in files:
            if nome.endswith((".xml", ".json", ".yaml")):
                with open(os.path.join(radice, nome), encoding="utf-8-sig", errors="ignore") as f:
                    # "…_value@OData.Community.Display…" nei flussi è un'annotazione OData, non un indirizzo
                    trovati = {e for e in EMAIL.findall(f.read()) if e != SEGNAPOSTO and "@OData." not in e}
                if trovati:
                    print(f"ATTENZIONE: indirizzi in {os.path.join(radice, nome)}")
    print(f"Fatto: {cambiati} modifiche")


if __name__ == "__main__":
    main(sys.argv[1])
