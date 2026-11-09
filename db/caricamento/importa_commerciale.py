"""Valida snapshot CSV commerciali; --applica li importa usando psql e PG*.

Ogni contratto incluso deve avere TUTTE le sue righe. Le dimensioni devono
esistere gia nel DB. Non importa anagrafiche e non modifica lo storico < 2026.
"""
import argparse
import csv
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import re
import subprocess
import sys

CONTRATTO = ('id_contratto,edizione,id_espositore,codice_stand,stato,data_firma,'
             'imponibile_listino,sconto_pct,imponibile,acconto_scadenza,'
             'acconto_pagato_il,saldo_scadenza,saldo_pagato_il,rinnovo').split(',')
RIGA = 'id_contratto,riga,codice_voce,descrizione,quantita,prezzo_unitario,importo'.split(',')


def leggi(path, colonne):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != colonne:
            raise ValueError(f'{Path(path).name}: intestazione diversa dal formato concordato')
        result = []
        for n, row in enumerate(reader, 2):
            if None in row or any(v is None for v in row.values()):
                raise ValueError(f'{Path(path).name}: numero colonne errato alla riga {n}')
            row = {k: v.strip() for k, v in row.items()}
            if any('\x00' in v for v in row.values()):
                raise ValueError('Carattere NUL non ammesso')
            result.append(row)
        return result


def numero(value, precisione, scala):
    if not re.fullmatch(r'-?\d+(?:\.\d+)?', value):
        raise ValueError('Decimale richiesto con punto, senza simboli valuta')
    try:
        n = Decimal(value)
        if n != n.quantize(Decimal(1).scaleb(-scala)) or abs(n) >= Decimal(10) ** (precisione-scala):
            raise ValueError('Decimale fuori precisione SQL')
        return n
    except InvalidOperation as exc:
        raise ValueError('Decimale non valido') from exc


def valida(contratti, righe):
    if not contratti or not righe:
        raise ValueError('Export vuoto: servono contratti e relative righe complete')
    ids, occupati, totali, chiavi = {}, set(), {}, set()
    for c in contratti:
        cid = c['id_contratto']
        if not re.fullmatch(r'C\d{4}-\d{4}', cid) or cid in ids:
            raise ValueError('Codice contratto invalido o duplicato')
        if not re.fullmatch(r'\d{4}', c['edizione']) or int(c['edizione']) < 2026 or cid[1:5] != c['edizione']:
            raise ValueError('Import consentito solo per edizioni dal 2026, coerenti con il codice')
        for field, length in [('id_espositore', 10), ('codice_stand', 10)]:
            if not c[field] or len(c[field]) > length:
                raise ValueError(f'{field}: codice vuoto o troppo lungo')
        if c['stato'] not in ('preventivo', 'firmato', 'annullato'):
            raise ValueError('Stato non valido')
        if c['rinnovo'] not in ('true', 'false'):
            raise ValueError('Rinnovo deve essere true/false')
        for field in ('data_firma', 'acconto_scadenza', 'acconto_pagato_il', 'saldo_scadenza', 'saldo_pagato_il'):
            if c[field] and (not re.fullmatch(r'\d{4}-\d{2}-\d{2}', c[field]) or not date.fromisoformat(c[field])):
                raise ValueError('Data non valida')
        if c['stato'] == 'firmato' and not c['data_firma']:
            raise ValueError('Firmato senza data firma')
        lordo = numero(c['imponibile_listino'], 12, 2)
        netto = numero(c['imponibile'], 12, 2)
        sconto = numero(c['sconto_pct'], 5, 4)
        if min(lordo, netto) < 0 or not 0 <= sconto <= 1:
            raise ValueError('Importi negativi o sconto fuori intervallo')
        if netto != (lordo * (1-sconto)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP):
            raise ValueError('Imponibile diverso da listino meno sconto')
        key = (c['edizione'], c['codice_stand'])
        if c['stato'] != 'annullato':
            if key in occupati:
                raise ValueError('Due contratti non annullati sullo stesso stand/edizione')
            occupati.add(key)
        ids[cid], totali[cid] = c, Decimal(0)
    for r in righe:
        cid = r['id_contratto']
        if cid not in ids:
            raise ValueError('Riga senza contratto nel medesimo export')
        if not re.fullmatch(r'[1-9]\d*', r['riga']) or int(r['riga']) > 32767:
            raise ValueError('Numero riga fuori intervallo smallint positivo')
        key = (cid, int(r['riga']))
        if key in chiavi:
            raise ValueError('Numero riga duplicato nel contratto')
        chiavi.add(key)
        if not r['codice_voce'] or len(r['codice_voce']) > 20 or not r['descrizione']:
            raise ValueError('Codice voce o descrizione non validi')
        q = numero(r['quantita'], 10, 2)
        p = numero(r['prezzo_unitario'], 12, 2)
        imp = numero(r['importo'], 12, 2)
        if q <= 0 or imp != (q*p).quantize(Decimal('.01'), rounding=ROUND_HALF_UP):
            raise ValueError('Quantita non positiva o importo riga incoerente')
        totali[cid] += imp
    for cid, c in ids.items():
        if not any(k[0] == cid for k in chiavi) or totali[cid] != Decimal(c['imponibile_listino']):
            raise ValueError('Righe mancanti o somma righe diversa dal listino')


def valore(value):
    # Hex UTF-8: nessun testo CSV puo diventare SQL o metacomando psql.
    return "convert_from(decode('" + value.encode('utf-8').hex() + "','hex'),'UTF8')"


def sql_importazione(contratti, righe):
    def insert(table, rows, columns, types):
        values = []
        for row in rows:
            values.append('(' + ','.join('NULL' if not row[c] else valore(row[c])+'::'+types[c]
                                        for c in columns) + ')')
        return f'INSERT INTO {table} ({",".join(columns)}) VALUES\n' + ',\n'.join(values) + ';'
    ct = {c: 'text' for c in CONTRATTO}
    ct.update({c: 'date' for c in CONTRATTO if c.endswith('_il') or c.endswith('_scadenza') or c == 'data_firma'})
    ct.update(edizione='smallint', imponibile_listino='numeric', sconto_pct='numeric', imponibile='numeric', rinnovo='boolean')
    rt = {c: 'text' for c in RIGA}
    rt.update(riga='smallint', quantita='numeric', prezzo_unitario='numeric', importo='numeric')
    updates = ','.join(f'{c}=EXCLUDED.{c}' for c in CONTRATTO if c != 'id_contratto')
    return '\n'.join([
        'BEGIN;', 'SET LOCAL search_path = arcade, pg_catalog;',
        'LOCK TABLE arcade.contratto, arcade.riga_contratto IN SHARE ROW EXCLUSIVE MODE;',
        'CREATE TEMP TABLE import_contratto (LIKE arcade.contratto INCLUDING DEFAULTS) ON COMMIT DROP;',
        'CREATE TEMP TABLE import_riga (LIKE arcade.riga_contratto INCLUDING DEFAULTS) ON COMMIT DROP;',
        insert('import_contratto', contratti, CONTRATTO, ct),
        insert('import_riga', righe, RIGA, rt),
        # Prima annulla i contratti dello snapshot: permette un cambio stand
        # nello stesso batch senza collisioni transitorie dell'indice parziale.
        "UPDATE arcade.contratto SET stato='annullato' WHERE id_contratto IN (SELECT id_contratto FROM import_contratto);",
        f'INSERT INTO arcade.contratto ({",".join(CONTRATTO)}) SELECT {",".join(CONTRATTO)} FROM import_contratto WHERE true ON CONFLICT (id_contratto) DO UPDATE SET {updates};',
        'DELETE FROM arcade.riga_contratto WHERE id_contratto IN (SELECT id_contratto FROM import_contratto);',
        f'INSERT INTO arcade.riga_contratto ({",".join(RIGA)}) SELECT {",".join(RIGA)} FROM import_riga;',
        'COMMIT;',
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contratti', required=True, type=Path)
    parser.add_argument('--righe', required=True, type=Path)
    parser.add_argument('--applica', action='store_true', help='Scrive nel DB configurato con PG*; default solo validazione')
    parser.add_argument('--psql', default='psql', help='Percorso eseguibile psql')
    args = parser.parse_args()
    try:
        contratti, righe = leggi(args.contratti, CONTRATTO), leggi(args.righe, RIGA)
        valida(contratti, righe)
        print(f'Validazione CSV OK: {len(contratti)} contratti, {len(righe)} righe.')
        if args.applica:
            result = subprocess.run([args.psql, '-X', '--no-password', '-q', '-v', 'ON_ERROR_STOP=1'],
                                    input=sql_importazione(contratti, righe).encode('utf-8'),
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode:
                # psql puo includere dati personali in DETAIL: non stamparli.
                raise ValueError('Import DB fallito: transazione non confermata; controllare connessione, permessi, FK e vincoli. Dettagli SQL non stampati per riservatezza.')
            print('Importazione confermata. Snapshot righe sostituito per i soli contratti inclusi.')
        else:
            print('Nessuna connessione o scrittura DB. FK e vincoli esistenti saranno verificati da PostgreSQL durante --applica.')
        return 0
    except (ValueError, OSError, csv.Error) as exc:
        print(f'Errore: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
