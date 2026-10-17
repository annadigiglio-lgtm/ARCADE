-- =====================================================================
-- ARCADE Milano - Viste KPI (unica definizione per API e Power BI)
-- Stato: BOZZA. Definizioni in docs/wiki/kpi.md, da concordare con BAD
-- Da eseguire dopo schema.sql e dati_base.sql
-- =====================================================================

SET search_path = arcade;

-- ---------------------------------------------------------------------
-- Base: ingressi validi (esito OK, biglietto esistente, no doppie letture)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_ingresso AS
SELECT p.id,
       p.edizione,
       p.rilevato_il,
       (p.rilevato_il AT TIME ZONE 'Europe/Rome')::date AS giorno,
       v.padiglione,
       p.codice_varco,
       p.id_biglietto,
       b.persone,
       b.tipo
FROM passaggio_varco p
JOIN varco v     ON v.codice = p.codice_varco
JOIN biglietto b ON b.id_biglietto = p.id_biglietto
WHERE p.valido;

-- ---------------------------------------------------------------------
-- KPI 1 - Visitatori
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_kpi_visitatori_giorno AS
SELECT edizione,
       giorno,
       sum(persone) AS visitatori,
       count(*)     AS biglietti
FROM (SELECT DISTINCT edizione, giorno, id_biglietto, persone FROM v_ingresso) bg
GROUP BY edizione, giorno;

CREATE OR REPLACE VIEW v_kpi_visitatori AS
SELECT i.edizione,
       count(*) AS ingressi_padiglioni,
       (SELECT sum(g.visitatori) FROM v_kpi_visitatori_giorno g
         WHERE g.edizione = i.edizione) AS visitatori_giornalieri,
       (SELECT sum(u.persone)
          FROM (SELECT DISTINCT x.id_biglietto, x.persone FROM v_ingresso x
                 WHERE x.edizione = i.edizione) u) AS visitatori_unici
FROM v_ingresso i
GROUP BY i.edizione;

-- ---------------------------------------------------------------------
-- KPI 2 - Presenze stimate e picco nei padiglioni
-- I varchi registrano solo gli ingressi. Una persona e' considerata
-- dentro un padiglione dal suo passaggio fino al passaggio successivo
-- della stessa giornata; dopo l'ultimo passaggio resta per
-- 'permanenza_minuti' (tabella parametro), senza superare la chiusura.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_permanenza AS
SELECT i.edizione,
       i.giorno,
       i.padiglione,
       i.id_biglietto,
       i.persone,
       i.rilevato_il AS entrata,
       COALESCE(
           lead(i.rilevato_il) OVER (PARTITION BY i.id_biglietto, i.giorno ORDER BY i.rilevato_il),
           LEAST(
               i.rilevato_il + make_interval(mins => (SELECT valore::int FROM parametro
                                                       WHERE nome = 'permanenza_minuti')),
               (i.giorno + e.ora_chiusura) AT TIME ZONE 'Europe/Rome'
           )
       ) AS uscita
FROM v_ingresso i
JOIN edizione e ON e.anno = i.edizione;

-- Presenze stimate ogni 5 minuti, per padiglione
-- (candidata a MATERIALIZED VIEW per le edizioni concluse)
CREATE OR REPLACE VIEW v_presenze_stimate AS
SELECT e.anno     AS edizione,
       t.istante,
       pd.codice  AS padiglione,
       COALESCE(sum(pm.persone), 0) AS presenti
FROM edizione e
CROSS JOIN LATERAL generate_series(e.data_inizio, e.data_fine, interval '1 day') AS d(giorno)
CROSS JOIN LATERAL generate_series(
           (d.giorno::date + e.ora_apertura) AT TIME ZONE 'Europe/Rome',
           (d.giorno::date + e.ora_chiusura) AT TIME ZONE 'Europe/Rome',
           interval '5 minutes') AS t(istante)
CROSS JOIN padiglione pd
LEFT JOIN v_permanenza pm
       ON pm.edizione = e.anno
      AND pm.padiglione = pd.codice
      AND pm.entrata <= t.istante
      AND pm.uscita  >  t.istante
GROUP BY e.anno, t.istante, pd.codice;

CREATE OR REPLACE VIEW v_kpi_picco_padiglione AS
SELECT DISTINCT ON (edizione, padiglione)
       edizione, padiglione, istante, presenti
FROM v_presenze_stimate
ORDER BY edizione, padiglione, presenti DESC, istante;

CREATE OR REPLACE VIEW v_kpi_picco_fiera AS
SELECT DISTINCT ON (edizione)
       edizione, istante, presenti
FROM (SELECT edizione, istante, sum(presenti) AS presenti
        FROM v_presenze_stimate
       GROUP BY edizione, istante) tot
ORDER BY edizione, presenti DESC, istante;

-- ---------------------------------------------------------------------
-- KPI 3 - Saturazione degli spazi (padiglione NULL = totale fiera)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_kpi_saturazione AS
SELECT e.anno AS edizione,
       s.padiglione,
       count(*)              AS stand_disponibili,
       count(c.id_contratto) AS stand_venduti,
       sum(s.mq)             AS mq_disponibili,
       COALESCE(sum(s.mq) FILTER (WHERE c.id_contratto IS NOT NULL), 0) AS mq_venduti,
       round(COALESCE(sum(s.mq) FILTER (WHERE c.id_contratto IS NOT NULL), 0) / sum(s.mq), 4)
                             AS saturazione_mq
FROM edizione e
JOIN stand s ON s.attivo_dal <= e.anno
LEFT JOIN contratto c
       ON c.edizione = e.anno
      AND c.codice_stand = s.codice_stand
      AND c.stato = 'firmato'
GROUP BY GROUPING SETS ((e.anno, s.padiglione), (e.anno));

-- ---------------------------------------------------------------------
-- KPI 4 - Ricavo per metro quadrato (padiglione NULL = totale fiera)
-- Ricavo = imponibile netto dei contratti (spazio, extra e sponsor)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_kpi_ricavo_mq AS
SELECT c.edizione,
       s.padiglione,
       sum(c.imponibile) AS ricavo,
       sum(s.mq)         AS mq_venduti,
       round(sum(c.imponibile) / sum(s.mq), 2) AS ricavo_per_mq
FROM contratto c
JOIN stand s ON s.codice_stand = c.codice_stand
WHERE c.stato = 'firmato'
GROUP BY GROUPING SETS ((c.edizione, s.padiglione), (c.edizione));

-- ---------------------------------------------------------------------
-- KPI 5 - Costo per contatto (per espositore)
-- Costo = imponibile del contratto; contatti = lead raccolti allo stand
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_kpi_costo_contatto AS
SELECT c.edizione,
       c.id_espositore,
       c.codice_stand,
       c.imponibile,
       count(k.id_contatto) AS contatti,
       round(c.imponibile / NULLIF(count(k.id_contatto), 0), 2) AS costo_per_contatto
FROM contratto c
LEFT JOIN contatto_stand k
       ON k.edizione = c.edizione
      AND k.codice_stand = c.codice_stand
WHERE c.stato = 'firmato'
GROUP BY c.id_contratto;

-- Valore complessivo della fiera: solo stand che hanno raccolto contatti
CREATE OR REPLACE VIEW v_kpi_costo_contatto_fiera AS
SELECT edizione,
       count(*)         AS stand_con_contatti,
       sum(contatti)    AS contatti,
       round(sum(imponibile) / sum(contatti), 2) AS costo_per_contatto
FROM v_kpi_costo_contatto
WHERE contatti > 0
GROUP BY edizione;

-- ---------------------------------------------------------------------
-- Viste di supporto per il portale espositori
-- ---------------------------------------------------------------------

-- Visite per stand e per ora, senza valori anomali
CREATE OR REPLACE VIEW v_visite_stand_ora AS
SELECT edizione,
       codice_stand,
       date_trunc('hour', rilevato_il AT TIME ZONE 'Europe/Rome') AS ora,
       sum(quantita) AS scansioni
FROM scansione_stand
WHERE anomalia IS NULL
GROUP BY edizione, codice_stand, date_trunc('hour', rilevato_il AT TIME ZONE 'Europe/Rome');

-- Contatti visibili all'espositore: l'email compare solo con consenso
-- e solo se il contatto e' sicuramente maggiorenne (tutela minori)
CREATE OR REPLACE VIEW v_contatti_espositore AS
SELECT k.id_contatto,
       k.edizione,
       k.id_espositore,
       k.codice_stand,
       k.raccolto_il,
       CASE WHEN k.consenso_marketing AND NOT COALESCE(f.minorenne, true)
            THEN k.email END AS email,
       k.fascia_eta,
       k.provincia,
       k.interesse
FROM contatto_stand k
LEFT JOIN fascia_eta f ON f.codice = k.fascia_eta;
