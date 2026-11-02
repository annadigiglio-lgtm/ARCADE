-- Generato da db/prepara_pubblicazione_supabase.ps1: non modificare questo file a mano.
-- Eseguire come proprietario dello schema arcade (postgres) nello SQL Editor Supabase.
-- Aggiorna le viste KPI e aggiunge le viste/funzioni API; non ricrea tabelle e non cancella dati.
BEGIN;
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
           lead(i.rilevato_il) OVER (PARTITION BY i.id_biglietto, i.giorno ORDER BY i.rilevato_il, i.id),
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

-- Dettaglio dei contatti visibile all'espositore: solo contatti con consenso,
-- email disponibile e maggiorenni con fascia d'eta' nota. I minori e i record
-- senza consenso restano disponibili solo nei conteggi aggregati.
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
LEFT JOIN fascia_eta f ON f.codice = k.fascia_eta
WHERE k.consenso_marketing
  AND k.email IS NOT NULL
  AND f.minorenne = false;

-- =====================================================================
-- ARCADE Milano - Viste e funzioni lette dalle API (cruscotto e portale)
-- Concordate tra DB e API il 2026-10-23: docs/wiki/viste-api.md
-- Da eseguire dopo schema.sql, dati_base.sql e viste_kpi.sql
-- =====================================================================

SET search_path = arcade;

-- ---------------------------------------------------------------------
-- Cruscotto staff
-- Tutte le funzioni ricevono un istante: in fiera e' "adesso", nella demo
-- e' l'ora simulata decisa dall'API. Nessun numero guarda oltre quell'istante,
-- tranne il modello di permanenza (stesso di v_permanenza in viste_kpi.sql).
-- ---------------------------------------------------------------------

-- Permanenze nei padiglioni nella giornata di un istante:
-- dentro dal passaggio fino al passaggio successivo dello stesso biglietto;
-- dopo l'ultimo passaggio resta 'permanenza_minuti', senza superare la chiusura.
CREATE OR REPLACE FUNCTION permanenze_giorno(p_istante timestamptz)
RETURNS TABLE (edizione smallint, padiglione varchar, persone smallint, entrata timestamptz, uscita timestamptz)
LANGUAGE sql STABLE AS $$
    WITH par AS (
        SELECT e.anno,
               d.giorno::timestamp AT TIME ZONE 'Europe/Rome'                    AS inizio_giorno,
               (d.giorno + 1)::timestamp AT TIME ZONE 'Europe/Rome'              AS fine_giorno,
               (d.giorno + e.ora_chiusura) AT TIME ZONE 'Europe/Rome'            AS chiusura,
               make_interval(mins => (SELECT valore::int FROM parametro
                                       WHERE nome = 'permanenza_minuti'))      AS permanenza
        FROM (SELECT (p_istante AT TIME ZONE 'Europe/Rome')::date AS giorno) d
        JOIN edizione e ON d.giorno BETWEEN e.data_inizio AND e.data_fine
    )
    SELECT i.edizione, i.padiglione, i.persone, i.rilevato_il,
           coalesce(lead(i.rilevato_il) OVER (PARTITION BY i.id_biglietto ORDER BY i.rilevato_il, i.id),
                    least(i.rilevato_il + par.permanenza, par.chiusura))
    FROM v_ingresso i, par
    WHERE i.edizione = par.anno
      AND i.rilevato_il >= par.inizio_giorno
      AND i.rilevato_il <  par.fine_giorno
$$;

-- Persone presenti in ogni padiglione in un istante
CREATE OR REPLACE FUNCTION presenze_al(p_istante timestamptz)
RETURNS TABLE (padiglione varchar, nome_padiglione text, presenti bigint, istante timestamptz)
LANGUAGE sql STABLE AS $$
    SELECT pd.codice, pd.nome, coalesce(sum(pg.persone), 0), p_istante
    FROM padiglione pd
    LEFT JOIN permanenze_giorno(p_istante) pg
           ON pg.padiglione = pd.codice
          AND pg.entrata <= p_istante
          AND pg.uscita  >  p_istante
    GROUP BY pd.codice, pd.nome
    ORDER BY pd.codice
$$;

-- Curva delle presenze della giornata, ogni 5 minuti, dall'apertura fino all'istante
CREATE OR REPLACE FUNCTION andamento_al(p_istante timestamptz)
RETURNS TABLE (istante timestamptz, padiglione varchar, presenti bigint)
LANGUAGE sql STABLE AS $$
    WITH par AS (
        SELECT (d.giorno + e.ora_apertura) AT TIME ZONE 'Europe/Rome' AS apertura,
               (d.giorno + e.ora_chiusura) AT TIME ZONE 'Europe/Rome' AS chiusura
        FROM (SELECT (p_istante AT TIME ZONE 'Europe/Rome')::date AS giorno) d
        JOIN edizione e ON d.giorno BETWEEN e.data_inizio AND e.data_fine
    ),
    istanti AS (
        SELECT generate_series(par.apertura, least(p_istante, par.chiusura), interval '5 minutes') AS t
        FROM par
    ),
    pg AS (SELECT * FROM permanenze_giorno(p_istante))
    SELECT s.t, pd.codice, coalesce(sum(pg.persone), 0)
    FROM istanti s
    CROSS JOIN padiglione pd
    LEFT JOIN pg ON pg.padiglione = pd.codice AND pg.entrata <= s.t AND pg.uscita > s.t
    GROUP BY s.t, pd.codice
    ORDER BY s.t, pd.codice
$$;

-- Ingressi per ora e padiglione nella giornata, fino all'istante
CREATE OR REPLACE FUNCTION ingressi_al(p_istante timestamptz)
RETURNS TABLE (ora timestamptz, padiglione varchar, ingressi bigint, persone bigint)
LANGUAGE sql STABLE AS $$
    SELECT date_trunc('hour', i.rilevato_il, 'Europe/Rome'), i.padiglione, count(*), sum(i.persone)
    FROM v_ingresso i
    WHERE i.rilevato_il >= (p_istante AT TIME ZONE 'Europe/Rome')::date::timestamp AT TIME ZONE 'Europe/Rome'
      AND i.rilevato_il <= p_istante
    GROUP BY 1, 2
    ORDER BY 1, 2
$$;

-- Totali della giornata fino all'istante: visitatori, ingressi, picco raggiunto finora
CREATE OR REPLACE FUNCTION giornata_al(p_istante timestamptz)
RETURNS TABLE (giorno date, visitatori bigint, ingressi bigint, picco_presenti bigint, picco_istante timestamptz)
LANGUAGE sql STABLE AS $$
    WITH oggi AS (
        SELECT i.id_biglietto, i.persone
        FROM v_ingresso i
        WHERE i.rilevato_il >= (p_istante AT TIME ZONE 'Europe/Rome')::date::timestamp AT TIME ZONE 'Europe/Rome'
          AND i.rilevato_il <= p_istante
    ),
    picco AS (
        SELECT a.istante, sum(a.presenti)::bigint AS presenti
        FROM andamento_al(p_istante) a
        GROUP BY a.istante
        ORDER BY presenti DESC, a.istante
        LIMIT 1
    )
    SELECT (p_istante AT TIME ZONE 'Europe/Rome')::date,
           (SELECT coalesce(sum(u.persone), 0) FROM (SELECT DISTINCT id_biglietto, persone FROM oggi) u),
           (SELECT count(*) FROM oggi),
           (SELECT presenti FROM picco),
           (SELECT istante FROM picco)
$$;

-- ---------------------------------------------------------------------
-- Portale espositori
-- Ogni vista ha id_espositore: l'API filtra SEMPRE con l'id preso dal token.
-- Nessun dato personale: niente nomi, email solo tramite v_contatti_espositore.
-- ---------------------------------------------------------------------

-- Visite al proprio stand per giorno e ora (scansioni valide)
CREATE OR REPLACE VIEW v_espositore_visite_ora AS
SELECT c.id_espositore,
       s.edizione,
       s.codice_stand,
       (s.rilevato_il AT TIME ZONE 'Europe/Rome')::date   AS giorno,
       date_trunc('hour', s.rilevato_il, 'Europe/Rome')    AS ora,
       sum(s.quantita)                                     AS scansioni
FROM scansione_stand s
JOIN contratto c
  ON c.edizione = s.edizione
 AND c.codice_stand = s.codice_stand
 AND c.stato = 'firmato'
WHERE s.anomalia IS NULL
GROUP BY c.id_espositore, s.edizione, s.codice_stand, 4, 5;

-- Riepilogo per edizione: stand, spesa, visite, contatti, costo per contatto,
-- ora di punta e media delle visite nel padiglione (dato aggregato, non di un concorrente)
CREATE OR REPLACE VIEW v_espositore_riepilogo AS
WITH visite AS (
    SELECT edizione, codice_stand, sum(quantita) AS visite
    FROM scansione_stand
    WHERE anomalia IS NULL
    GROUP BY edizione, codice_stand
),
contatti AS (
    SELECT k.edizione,
           k.codice_stand,
           count(*) AS contatti,
           count(*) FILTER (
               WHERE k.consenso_marketing
                 AND k.email IS NOT NULL
                 AND f.minorenne = false
           ) AS contatti_con_consenso
    FROM contatto_stand k
    LEFT JOIN fascia_eta f ON f.codice = k.fascia_eta
    GROUP BY k.edizione, k.codice_stand
),
punta AS (
    SELECT DISTINCT ON (edizione, codice_stand) edizione, codice_stand, ora AS ora_di_punta
    FROM v_espositore_visite_ora
    ORDER BY edizione, codice_stand, scansioni DESC, ora
),
media AS (
    SELECT v.edizione, s.padiglione, round(avg(v.visite)) AS media_visite_padiglione
    FROM visite v
    JOIN stand s ON s.codice_stand = v.codice_stand
    GROUP BY v.edizione, s.padiglione
)
SELECT c.id_espositore,
       c.edizione,
       e.ragione_sociale,
       c.codice_stand,
       s.padiglione,
       p.nome                                         AS nome_padiglione,
       s.mq,
       s.posizione,
       c.imponibile,
       v.visite,                                      -- NULL = visite non rilevate (es. 2024)
       CASE WHEN v.visite IS NULL AND k.contatti IS NULL THEN NULL
            ELSE coalesce(k.contatti, 0) END                 AS contatti,
       CASE WHEN v.visite IS NULL AND k.contatti IS NULL THEN NULL
            ELSE coalesce(k.contatti_con_consenso, 0) END    AS contatti_con_consenso,
       round(c.imponibile / NULLIF(k.contatti, 0), 2) AS costo_per_contatto,   -- stessa formula di v_kpi_costo_contatto
       pu.ora_di_punta,
       m.media_visite_padiglione
FROM contratto c
JOIN espositore e  ON e.id_espositore = c.id_espositore
JOIN stand s       ON s.codice_stand = c.codice_stand
JOIN padiglione p  ON p.codice = s.padiglione
LEFT JOIN visite v   ON v.edizione = c.edizione AND v.codice_stand = c.codice_stand
LEFT JOIN contatti k ON k.edizione = c.edizione AND k.codice_stand = c.codice_stand
LEFT JOIN punta pu   ON pu.edizione = c.edizione AND pu.codice_stand = c.codice_stand
LEFT JOIN media m    ON m.edizione = c.edizione AND m.padiglione = s.padiglione
WHERE c.stato = 'firmato';

-- Confronto tra edizioni. Visite e contatti esistono solo dal 2025:
-- per il 2024 resta il traffico del padiglione (ingressi validi)
CREATE OR REPLACE VIEW v_espositore_confronto AS
SELECT r.id_espositore,
       r.edizione,
       r.codice_stand,
       r.padiglione,
       r.mq,
       r.imponibile,
       r.visite,
       r.contatti,
       ip.ingressi AS ingressi_padiglione
FROM v_espositore_riepilogo r
LEFT JOIN (SELECT edizione, padiglione, count(*) AS ingressi
           FROM v_ingresso
           GROUP BY edizione, padiglione) ip
       ON ip.edizione = r.edizione AND ip.padiglione = r.padiglione;

-- Proposta di rinnovo sullo stesso stand con il listino dell'edizione successiva.
-- Prezzo stimato = solo area (mq x prezzo al mq del padiglione + maggiorazione di posizione),
-- senza extra e prima di eventuali sconti.
CREATE OR REPLACE VIEW v_espositore_rinnovo AS
SELECT c.id_espositore,
       c.edizione + 1                     AS edizione_rinnovo,
       c.codice_stand,
       s.padiglione,
       s.mq,
       s.posizione,
       round(s.mq * sp.prezzo_unitario * (1 + coalesce(mg.prezzo_unitario, 0)), 2) AS prezzo_area_stimato,
       make_date(c.edizione + 1, 3, 31)   AS prelazione_fino_al,   -- condizione COND-PRELAZ del listino
       EXISTS (SELECT 1 FROM contratto n
                WHERE n.edizione = c.edizione + 1
                  AND n.id_espositore = c.id_espositore
                  AND n.stato <> 'annullato')  AS gia_rinnovato
FROM contratto c
JOIN stand s ON s.codice_stand = c.codice_stand
JOIN voce_listino sp
  ON sp.edizione = c.edizione + 1 AND sp.codice = 'SPAZIO-' || s.padiglione
LEFT JOIN voce_listino mg
  ON mg.edizione = c.edizione + 1 AND mg.codice = 'MAGG-' || upper(s.posizione)
WHERE c.stato = 'firmato';

-- ---------------------------------------------------------------------
-- Permessi: l'API (utente bid_app) deve poter eseguire le funzioni.
-- Le viste nuove ricevono i permessi dalle regole di default (guida-supabase.md).
-- Il controllo evita errori nel database locale, dove bid_app non esiste.
-- ---------------------------------------------------------------------
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'bid_app') THEN
        GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA arcade TO bid_app;
    END IF;
END
$$;

GRANT SELECT ON ALL TABLES IN SCHEMA arcade TO bid_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA arcade TO bid_app;
SELECT * FROM arcade.presenze_al('2025-12-20T11:55:00+01:00'::timestamptz);
COMMIT;