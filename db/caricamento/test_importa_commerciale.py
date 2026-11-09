"""Casi sintetici; nessun dato cliente e nessuna connessione DB."""
import copy
import unittest
from importa_commerciale import CONTRATTO, valida, sql_importazione


class ImportCommercialeTest(unittest.TestCase):
    def setUp(self):
        c = dict.fromkeys(CONTRATTO, '')
        c.update(id_contratto='C2026-9001', edizione='2026', id_espositore='TEST001',
                 codice_stand='TEST-A01', stato='firmato', data_firma='2026-11-09',
                 imponibile_listino='100.00', sconto_pct='0.10', imponibile='90.00', rinnovo='false')
        self.c = [c]
        self.r = [dict(id_contratto=c['id_contratto'], riga='17', codice_voce='TEST',
                       descrizione='Voce sintetica', quantita='2', prezzo_unitario='50', importo='100')]

    def test_valido_con_riga_17(self):
        valida(self.c, self.r)

    def test_vuoti(self):
        with self.assertRaises(ValueError):
            valida([], [])

    def test_duplicato(self):
        with self.assertRaises(ValueError):
            valida(self.c, self.r + self.r)

    def test_totale_errato(self):
        self.c[0]['imponibile_listino'] = '101'
        self.c[0]['imponibile'] = '90.90'
        with self.assertRaises(ValueError):
            valida(self.c, self.r)

    def test_firma_obbligatoria(self):
        self.c[0]['data_firma'] = ''
        with self.assertRaises(ValueError):
            valida(self.c, self.r)

    def test_storico_protetto(self):
        self.c[0].update(id_contratto='C2025-9001', edizione='2025')
        with self.assertRaises(ValueError):
            valida(self.c, self.r)

    def test_stand_occupato(self):
        secondo = copy.deepcopy(self.c[0])
        secondo['id_contratto'] = 'C2026-9002'
        with self.assertRaises(ValueError):
            valida(self.c + [secondo], self.r)

    def test_precisione_non_troncata(self):
        self.r[0]['importo'] = '100.001'
        with self.assertRaises(ValueError):
            valida(self.c, self.r)

    def test_riga_estranea(self):
        self.r[0]['id_contratto'] = 'C2026-9999'
        with self.assertRaises(ValueError):
            valida(self.c, self.r)

    def test_testo_non_diventa_sql(self):
        testo = "Test'); DROP TABLE arcade.contratto; --\n\\! comando"
        self.r[0]['descrizione'] = testo
        valida(self.c, self.r)
        sql = sql_importazione(self.c, self.r)
        self.assertNotIn(testo, sql)
        self.assertIn(testo.encode().hex(), sql)
        self.assertTrue(sql.startswith('BEGIN;'))
        self.assertTrue(sql.endswith('COMMIT;'))


if __name__ == '__main__':
    unittest.main()
