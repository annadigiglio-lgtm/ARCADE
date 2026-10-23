"""Esporta i fogli di ARCADE_Commerciale.xlsx in file CSV (UTF-8, separatore virgola).

Nessuna pulizia: i valori restano come nel file del cliente, la pulizia avviene in SQL
(02_trasforma.sql). Date in formato AAAA-MM-GG, booleani true/false, celle vuote vuote.

Uso: python excel_in_csv.py <file.xlsx> <cartella di uscita>
Richiede: pip install openpyxl
"""
import csv
import datetime
import sys
from pathlib import Path

import openpyxl


def valore(v):
    if v is None:
        return ''
    if isinstance(v, bool):  # prima di int: in Python bool è un sottotipo di int
        return 'true' if v else 'false'
    if isinstance(v, datetime.datetime):
        if v.time() == datetime.time(0):
            return v.date().isoformat()
        return v.isoformat(sep=' ')
    if isinstance(v, datetime.date):
        return v.isoformat()
    return str(v)


def main(file_excel, cartella_uscita):
    uscita = Path(cartella_uscita)
    uscita.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.load_workbook(file_excel, read_only=True, data_only=True)
    for foglio in wb.worksheets:
        if foglio.title == 'LEGGIMI':
            continue
        righe = 0
        with open(uscita / f'{foglio.title}.csv', 'w', encoding='utf-8', newline='') as f:
            scrittore = csv.writer(f)
            for riga in foglio.iter_rows(values_only=True):
                if all(v is None for v in riga):
                    continue
                scrittore.writerow([valore(v) for v in riga])
                righe += 1
        print(f'{foglio.title}: {righe - 1} righe')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Uso: python excel_in_csv.py <file.xlsx> <cartella di uscita>')
    main(sys.argv[1], sys.argv[2])
