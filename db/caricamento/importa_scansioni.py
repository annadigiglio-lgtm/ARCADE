"""Valida CSV di eventi app; --applica importa usando psql e variabili PG*."""
import argparse
import csv
from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys
from uuid import UUID

from importa_commerciale import leggi, valore

COLONNE = ['g5_id_scansione', 'edizione', 'codice_stand', 'rilevato_il']


def valida(rows):
    if not rows:
        raise ValueError('Export vuoto')
    eventi = {}
    for row in rows:
        try:
            guid = str(UUID(row['g5_id_scansione']))
        except ValueError as exc:
            raise ValueError('GUID scansione non valido') from exc
        if UUID(guid).int == 0:
            raise ValueError('GUID nullo non ammesso')
        if not re.fullmatch(r'\d{4}', row['edizione']) or not 2026 <= int(row['edizione']) <= 9999:
            raise ValueError('Edizione consentita dal 2026')
        if not row['codice_stand'] or len(row['codice_stand']) > 10:
            raise ValueError('Codice stand non valido')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})', row['rilevato_il']):
            raise ValueError('Timestamp ISO 8601 richiesto con secondi e fuso esplicito')
        dt = datetime.fromisoformat(row['rilevato_il'])
        if dt.utcoffset() is None:
            raise ValueError('Fuso obbligatorio')
        payload = (row['edizione'], row['codice_stand'], dt)
        if guid in eventi and eventi[guid] != payload:
            raise ValueError('GUID ripetuto con dati diversi')
        eventi[guid] = payload
        row['g5_id_scansione'] = guid


def sql_importazione(rows):
    # Deduplica per UUID; istanti con fusi diversi sono confrontati da PostgreSQL.
    unique = {r['g5_id_scansione']: r for r in rows}
    values = ',\n'.join('(' + ','.join(valore(r[c]) + '::' + t for c, t in
        zip(COLONNE, ['uuid', 'smallint', 'varchar(10)', 'timestamptz'])) + ')'
        for r in unique.values())
    return '\n'.join([
        'BEGIN;', "SET LOCAL statement_timeout='60s';",
        "SET LOCAL lock_timeout='10s';",
        'LOCK TABLE arcade.scansione_stand IN SHARE ROW EXCLUSIVE MODE;',
        'CREATE TEMP TABLE import_scansione (g5_id_scansione uuid PRIMARY KEY, edizione smallint, codice_stand varchar(10), rilevato_il timestamptz) ON COMMIT DROP;',
        'INSERT INTO import_scansione VALUES ' + values + ';',
        """DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM import_scansione i
          JOIN arcade.scansione_stand s USING(g5_id_scansione)
          WHERE (s.edizione,s.codice_stand,s.rilevato_il,s.quantita,s.origine,s.anomalia)
            IS DISTINCT FROM (i.edizione,i.codice_stand,i.rilevato_il,1,'app'::text,NULL::text))
        THEN RAISE EXCEPTION 'GUID gia presente con contenuto diverso'; END IF;
        END $$;""",
        "INSERT INTO arcade.scansione_stand (g5_id_scansione,edizione,codice_stand,rilevato_il,quantita,origine) SELECT g5_id_scansione,edizione,codice_stand,rilevato_il,1,'app' FROM import_scansione ON CONFLICT (g5_id_scansione) DO NOTHING;",
        'COMMIT;'
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scansioni', type=Path, required=True)
    parser.add_argument('--applica', action='store_true')
    parser.add_argument('--psql', default='psql')
    args = parser.parse_args()
    try:
        rows = leggi(args.scansioni, COLONNE)
        valida(rows)
        print(f'CSV valido: {len(rows)} righe, {len({r["g5_id_scansione"] for r in rows})} eventi distinti.')
        if args.applica:
            result = subprocess.run([args.psql, '-X', '-w', '-q', '-v', 'ON_ERROR_STOP=1'],
                input=sql_importazione(rows).encode('utf-8'), capture_output=True)
            if result.returncode:
                raise ValueError('Import non confermato: controllare migrazione, connessione, permessi, FK e GUID discordanti. Dettagli SQL omessi per riservatezza.')
            print('Import confermato; reinvii identici ignorati.')
        else:
            print('Nessuna connessione DB. Esistenza stand/edizione e GUID discordanti nel DB verificati solo con --applica.')
        return 0
    except (ValueError, OSError, csv.Error) as exc:
        print(f'Errore: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
