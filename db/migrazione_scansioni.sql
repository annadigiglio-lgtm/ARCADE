-- Eseguire come proprietario dello schema. Conserva righe e ID storici.
BEGIN;
ALTER TABLE arcade.scansione_stand ADD COLUMN IF NOT EXISTS g5_id_scansione uuid;
CREATE UNIQUE INDEX IF NOT EXISTS ux_scansione_sorgente
    ON arcade.scansione_stand (g5_id_scansione);
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint
                   WHERE conrelid='arcade.scansione_stand'::regclass
                     AND conname='ck_scansione_app_sorgente') THEN
        -- NOT VALID conserva eventuali eventi app preesistenti senza GUID.
        -- Il vincolo vale subito per ogni nuovo inserimento/aggiornamento.
        ALTER TABLE arcade.scansione_stand ADD CONSTRAINT ck_scansione_app_sorgente
            CHECK (origine <> 'app' OR (g5_id_scansione IS NOT NULL AND quantita=1)) NOT VALID;
    END IF;
END $$;
COMMIT;
