"""Test unita; con SCANSIONI_TEST_DB=1 anche PostgreSQL isolato (PG*)."""
import os
from pathlib import Path
import subprocess
import unittest
from importa_scansioni import valida, sql_importazione

ROOT = Path(__file__).resolve().parents[2]

def evento(**kw):
    return dict(g5_id_scansione='00000000-0000-4000-8000-000000000001', edizione='2026', codice_stand='TEST1', rilevato_il='2026-12-18T10:00:00+01:00', **kw)

class Validazione(unittest.TestCase):
    def test_reinvio(self):
        r=evento(); valida([r, r.copy()])
    def test_fusi_equivalenti(self):
        r=evento(); s=evento(); s['rilevato_il']='2026-12-18T09:00:00Z'; valida([r,s])
    def test_errori(self):
        for field,value in [('g5_id_scansione','no'),('g5_id_scansione','00000000-0000-0000-0000-000000000000'),('edizione','2025'),('rilevato_il','2026-12-18T10:00:00'),('codice_stand','')]:
            with self.subTest(field=field,value=value):
                r=evento(); r[field]=value
                with self.assertRaises(ValueError): valida([r])
    def test_collisione(self):
        r=evento(); s=evento(); s['codice_stand']='TEST2'
        with self.assertRaises(ValueError): valida([r,s])
    def test_vuoto(self):
        with self.assertRaises(ValueError): valida([])

@unittest.skipUnless(os.getenv('SCANSIONI_TEST_DB')=='1','PostgreSQL isolato non richiesto')
class Database(unittest.TestCase):
    @classmethod
    def run_sql(cls, sql, ok=True):
        r=subprocess.run([os.environ['TEST_PSQL'],'-X','-w','-At','-v','ON_ERROR_STOP=1'],input=sql.encode(),capture_output=True)
        if ok and r.returncode: raise AssertionError(r.stderr.decode(errors='replace'))
        if not ok and not r.returncode: raise AssertionError('Import avrebbe dovuto fallire')
        return r.stdout.decode().strip()
    @classmethod
    def setUpClass(cls):
        cls.run_sql((ROOT/'db/schema.sql').read_text())
        cls.run_sql("""INSERT INTO arcade.edizione VALUES(2026,'2026-12-18','2026-12-20','09:00','19:00');
INSERT INTO arcade.padiglione VALUES('T1','Test');
INSERT INTO arcade.stand VALUES('TEST1','T1',10,'linea',2026);
ALTER TABLE arcade.scansione_stand DROP CONSTRAINT ck_scansione_app_sorgente;
ALTER TABLE arcade.scansione_stand DROP COLUMN g5_id_scansione;
INSERT INTO arcade.scansione_stand(edizione,codice_stand,rilevato_il,quantita,origine) VALUES(2026,'TEST1','2026-12-18T08:00:00Z',7,'storico_orario'),(2026,'TEST1','2026-12-18T08:00:00Z',1,'app');""")
        migration=(ROOT/'db/migrazione_scansioni.sql').read_text()
        cls.run_sql(migration); cls.run_sql(migration)
    def test_importazione(self):
        r=evento(); valida([r]); sql=sql_importazione([r,r.copy()])
        self.run_sql(sql); self.run_sql(sql)
        self.assertEqual(self.run_sql('SELECT count(*),sum(quantita) FROM arcade.scansione_stand;'),'3|9')
        changed=evento(); changed['rilevato_il']='2026-12-18T11:00:00+01:00'
        self.run_sql(sql_importazione([changed]),ok=False)
        missing=evento(); missing['g5_id_scansione']='00000000-0000-4000-8000-000000000002'; missing['codice_stand']='MISSING'
        new=evento(); new['g5_id_scansione']='00000000-0000-4000-8000-000000000003'
        self.run_sql(sql_importazione([new,missing]),ok=False)
        self.assertEqual(self.run_sql('SELECT count(*),sum(quantita) FROM arcade.scansione_stand;'),'3|9')
        self.run_sql("INSERT INTO arcade.scansione_stand(edizione,codice_stand,rilevato_il,origine) VALUES(2026,'TEST1',now(),'app');",ok=False)
        self.assertEqual(self.run_sql('SELECT count(*) FROM arcade.scansione_stand WHERE g5_id_scansione IS NULL;'),'2')

if __name__=='__main__': unittest.main()
