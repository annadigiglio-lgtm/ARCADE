-- Eseguire dopo schema.sql e viste_kpi.sql in un DB di prova vuoto.
-- Tutte le fixture sono sintetiche e vengono annullate.
BEGIN;
SET search_path = arcade;
INSERT INTO edizione VALUES
 (2090,'2090-12-01','2090-12-03','09:00','19:00'),
 (2091,'2091-12-01','2091-12-03','09:00','19:00'),
 (2092,'2092-12-01','2092-12-03','09:00','19:00');
INSERT INTO padiglione VALUES ('T1','Test');
INSERT INTO stand VALUES ('TEST1','T1',10,'linea',2090),('TEST2','T1',10,'linea',2090),('TEST3','T1',10,'linea',2090);
INSERT INTO espositore (id_espositore,ragione_sociale,partita_iva) VALUES
 ('TEST1','Test uno','00000000001'),('TEST2','Test due','00000000002'),('TEST3','Test tre','00000000003');
INSERT INTO contratto (id_contratto,edizione,id_espositore,codice_stand,stato,data_firma,imponibile_listino,imponibile) VALUES
 ('TEST90A',2090,'TEST1','TEST1','firmato','2090-01-01',100,100),
 ('TEST90B',2090,'TEST1','TEST2','firmato','2090-01-01',100,100),
 ('TEST90C',2090,'TEST2','TEST3','firmato','2090-01-01',100,100),
 ('TEST91A',2091,'TEST1','TEST1','firmato','2091-01-01',100,100),
 ('TEST91B',2091,'TEST2','TEST2','preventivo',NULL,100,100),
 ('TEST91C',2091,'TEST3','TEST3','firmato','2091-01-01',100,100);
UPDATE contratto SET acconto_pagato_il='2091-01-02' WHERE id_contratto='TEST91A';
UPDATE contratto SET saldo_pagato_il='2091-01-03' WHERE id_contratto='TEST91C';
INSERT INTO tipo_biglietto VALUES ('TEST','Test',1,1);
INSERT INTO biglietto (id_biglietto,id_ordine,edizione,acquistato_il,canale,tipo,prezzo,persone) VALUES
 ('TESTB1','TESTO1',2091,'2091-01-01T23:30:00Z','Online','TEST',40,4),
 ('TESTB2','TESTO1',2091,'2091-01-02T10:00:00Z','Online','TEST',10,1),
 ('TESTB3','TESTO2',2091,'2091-01-02T10:00:00Z','Cassa','TEST',0,1);
INSERT INTO varco VALUES ('TESTVARCO','T1');
INSERT INTO passaggio_varco (edizione,rilevato_il,codice_varco,codice_letto,id_biglietto,esito_ok,anomalia) VALUES
 (2091,'2091-12-01T09:00:00Z','TESTVARCO','TESTB1','TESTB1',true,NULL),
 (2091,'2091-12-02T09:00:00Z','TESTVARCO','TESTB1','TESTB1',true,NULL),
 (2091,'2091-12-01T09:00:00Z','TESTVARCO','TESTB2','TESTB2',false,NULL),
 (2091,'2091-12-01T09:00:00Z','TESTVARCO','TESTB3','TESTB3',true,'DOPPIA_LETTURA');
DO $$
BEGIN
 IF NOT EXISTS (SELECT 1 FROM v_kpi_rinnovo WHERE edizione=2091
   AND espositori_precedenti=2 AND espositori_attuali=2 AND espositori_rinnovati=1
   AND espositori_persi=1 AND espositori_nuovi=1 AND tasso_rinnovo=0.5)
 THEN RAISE EXCEPTION 'Rinnovo: distinti/stati/rapporto errati'; END IF;
 IF NOT EXISTS (SELECT 1 FROM v_kpi_rinnovo WHERE edizione=2090 AND tasso_rinnovo IS NULL AND espositori_precedenti IS NULL)
 THEN RAISE EXCEPTION 'Prima edizione'; END IF;
 IF NOT EXISTS (SELECT 1 FROM v_kpi_conversione WHERE edizione=2091
   AND biglietti_venduti=3 AND biglietti_entrati=1 AND tasso_conversione=0.3333)
 THEN RAISE EXCEPTION 'Conversione: duplicati/letture invalide/Family'; END IF;
 IF NOT EXISTS (SELECT 1 FROM v_kpi_conversione WHERE edizione=2092 AND biglietti_venduti=0 AND tasso_conversione IS NULL)
 THEN RAISE EXCEPTION 'Edizione senza biglietti'; END IF;
 IF NOT EXISTS (SELECT 1 FROM v_vendite_biglietti_giorno WHERE edizione=2091 AND giorno='2091-01-02'
   AND canale='Online' AND biglietti=2 AND persone=5 AND ricavo_biglietti=50)
 THEN RAISE EXCEPTION 'Vendite: fuso/canale/prezzo Family'; END IF;
 IF NOT EXISTS (SELECT 1 FROM v_incassi_contratto WHERE id_contratto='TEST91A'
   AND stato_pagamenti='acconto_registrato' AND importo_incassato IS NULL)
 OR NOT EXISTS (SELECT 1 FROM v_incassi_contratto WHERE id_contratto='TEST91C' AND stato_pagamenti='saldo_registrato')
 OR NOT EXISTS (SELECT 1 FROM v_incassi_contratto WHERE id_contratto='TEST91B' AND stato_pagamenti='non_applicabile')
 THEN RAISE EXCEPTION 'Pagamenti: stato o importi inventati'; END IF;
END $$;
ROLLBACK;
