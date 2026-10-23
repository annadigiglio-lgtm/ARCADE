-- =====================================================================
-- Caricamento storico 2024-2025 - passo 3: verifica
-- Confronta i dati caricati con i "numeri di controllo" di docs/wiki/dati.md,
-- calcolati in modo indipendente sui file originali.
-- =====================================================================

\echo 'Verifica dei numeri di controllo:'

SELECT controllo, trovato, atteso,
       CASE WHEN trovato = atteso THEN 'OK' ELSE '<<< DIVERSO' END AS esito
FROM (VALUES
    ('espositori',                       (SELECT count(*) FROM espositore)::numeric,                                        135::numeric),
    ('stand',                            (SELECT count(*) FROM stand),                                                      130),
    ('voci di listino 2026',             (SELECT count(*) FROM voce_listino),                                               20),
    ('contratti 2024',                   (SELECT count(*) FROM contratto WHERE edizione = 2024),                            88),
    ('contratti 2025',                   (SELECT count(*) FROM contratto WHERE edizione = 2025),                            110),
    ('righe contratto',                  (SELECT count(*) FROM riga_contratto),                                             950),
    ('imponibile 2024',                  (SELECT sum(imponibile) FROM contratto WHERE edizione = 2024),                     706310.35),
    ('imponibile 2025',                  (SELECT sum(imponibile) FROM contratto WHERE edizione = 2025),                     821730.60),
    ('rinnovi 2025',                     (SELECT count(*) FROM contratto WHERE edizione = 2025 AND rinnovo),                70),
    ('biglietti 2024',                   (SELECT count(*) FROM biglietto WHERE edizione = 2024),                            35719),
    ('biglietti 2025',                   (SELECT count(*) FROM biglietto WHERE edizione = 2025),                            42556),
    ('persone sui biglietti 2024',       (SELECT sum(persone) FROM biglietto WHERE edizione = 2024),                        42979),
    ('persone sui biglietti 2025',       (SELECT sum(persone) FROM biglietto WHERE edizione = 2025),                        51259),
    ('passaggi 2024',                    (SELECT count(*) FROM passaggio_varco WHERE edizione = 2024),                      46824),
    ('passaggi 2025',                    (SELECT count(*) FROM passaggio_varco WHERE edizione = 2025),                      55992),
    ('doppie letture 2024',              (SELECT count(*) FROM passaggio_varco WHERE edizione = 2024 AND anomalia = 'DOPPIA_LETTURA'), 972),
    ('doppie letture 2025',              (SELECT count(*) FROM passaggio_varco WHERE edizione = 2025 AND anomalia = 'DOPPIA_LETTURA'), 1195),
    ('ingressi validi 2024',             (SELECT ingressi_padiglioni FROM v_kpi_visitatori WHERE edizione = 2024),          45622),
    ('ingressi validi 2025',             (SELECT ingressi_padiglioni FROM v_kpi_visitatori WHERE edizione = 2025),          54541),
    ('visitatori giornalieri 2024',      (SELECT visitatori_giornalieri FROM v_kpi_visitatori WHERE edizione = 2024),       46425),
    ('visitatori giornalieri 2025',      (SELECT visitatori_giornalieri FROM v_kpi_visitatori WHERE edizione = 2025),       55498),
    ('visitatori unici 2024',            (SELECT visitatori_unici FROM v_kpi_visitatori WHERE edizione = 2024),             41434),
    ('visitatori unici 2025',            (SELECT visitatori_unici FROM v_kpi_visitatori WHERE edizione = 2025),             49441),
    ('mq venduti 2024',                  (SELECT mq_venduti FROM v_kpi_saturazione WHERE edizione = 2024 AND padiglione IS NULL), 3028),
    ('mq venduti 2025',                  (SELECT mq_venduti FROM v_kpi_saturazione WHERE edizione = 2025 AND padiglione IS NULL), 3313),
    ('visite agli stand 2025 (valide)',  (SELECT sum(quantita) FROM scansione_stand WHERE anomalia IS NULL),               35301),
    ('contatti agli stand 2025',         (SELECT count(*) FROM contatto_stand),                                             1707),
    ('contratti non abbinati',           (SELECT count(*) FROM anomalia WHERE codice = 'A16' AND gestione LIKE 'Contratto NON%'), 0)
) AS v (controllo, trovato, atteso);

\echo 'Anomalie registrate:'

SELECT codice, count(*) AS righe_nel_registro, min(descrizione) AS esempio
FROM anomalia
GROUP BY codice
ORDER BY length(codice), codice;
