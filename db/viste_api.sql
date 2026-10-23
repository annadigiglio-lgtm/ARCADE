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
    SELECT edizione, codice_stand, count(*) AS contatti, count(email) AS contatti_con_consenso
    FROM v_contatti_espositore
    GROUP BY edizione, codice_stand
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
