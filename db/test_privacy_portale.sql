-- Solo database locale vuoto con schema.sql e viste_kpi.sql gia caricati.
-- Fixture sintetiche: nessun dato personale reale. Rollback finale.
BEGIN;
SET search_path=arcade;
INSERT INTO edizione VALUES (2090,'2090-12-01','2090-12-03','09:00','19:00');
INSERT INTO padiglione VALUES ('T1','Test privacy');
INSERT INTO stand VALUES ('TEST1','T1',10,'linea',2090);
INSERT INTO espositore(id_espositore,ragione_sociale,partita_iva)
 VALUES ('TEST1','Test privacy','00000000001');
INSERT INTO fascia_eta VALUES ('adulto',false,1),('minore',true,2);
INSERT INTO contatto_stand(id_contatto,edizione,codice_stand,id_espositore,raccolto_il,email,fascia_eta,consenso_marketing) VALUES
 ('TEST01',2090,'TEST1','TEST1','2090-12-01T10:00:00Z','adult@example.invalid','adulto',true),
 ('TEST02',2090,'TEST1','TEST1','2090-12-01T10:00:00Z','minor@example.invalid','minore',true),
 ('TEST03',2090,'TEST1','TEST1','2090-12-01T10:00:00Z','unknown@example.invalid',NULL,true),
 ('TEST04',2090,'TEST1','TEST1','2090-12-01T10:00:00Z','no-consent@example.invalid','adulto',false),
 ('TEST05',2090,'TEST1','TEST1','2090-12-01T10:00:00Z',NULL,'adulto',true);
DO $$ BEGIN
 IF (SELECT count(*) FROM v_contatti_espositore WHERE edizione=2090) <> 1
 OR NOT EXISTS (SELECT 1 FROM v_contatti_espositore WHERE id_contatto='TEST01')
 THEN RAISE EXCEPTION 'Filtro privacy non rispettato'; END IF;
 IF (SELECT count(*) FROM contatto_stand WHERE edizione=2090) <> 5
 THEN RAISE EXCEPTION 'I contatti esclusi dal dettaglio devono restare nello storico'; END IF;
END $$;
ROLLBACK;
