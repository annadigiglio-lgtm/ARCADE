-- =====================================================================
-- Caricamento storico 2024-2025 - passo 2: pulizia e caricamento nelle tabelle
-- Tutto in una transazione: se un comando fallisce non viene salvato niente.
-- I codici A1...A31 sono le anomalie di docs/wiki/dati.md.
--
-- ATTENZIONE: ricaricare cancella e riscrive i dati commerciali e di affluenza.
-- Quando arriveranno i contratti 2026 dalla sincronizzazione con Dataverse
-- questo script andrà limitato allo storico.
-- =====================================================================

BEGIN;

\echo 'Pulizia dei dati caricati in precedenza...'

DELETE FROM anomalia;
DELETE FROM contatto_stand;
DELETE FROM scansione_stand;
DELETE FROM passaggio_varco;
DELETE FROM biglietto;
DELETE FROM riga_contratto;
DELETE FROM contratto;
DELETE FROM espositore_alias;
DELETE FROM voce_listino;
DELETE FROM stand;
DELETE FROM espositore;

-- ---------------------------------------------------------------------
-- Commerciale
-- ---------------------------------------------------------------------
\echo 'Commerciale...'

INSERT INTO espositore (id_espositore, ragione_sociale, partita_iva, settore, citta, referente, email_referente)
SELECT trim(id_espositore), trim(ragione_sociale), trim(partita_iva), settore, citta, referente, email_referente
FROM s_espositori;

INSERT INTO stand (codice_stand, padiglione, mq, posizione, attivo_dal)
SELECT trim(codice_stand), padiglione, mq::numeric, posizione, attivo_dal::smallint
FROM s_planimetria;

INSERT INTO voce_listino (edizione, codice, descrizione, unita, prezzo_unitario, disponibilita, note)
SELECT 2026, codice, voce, unita, prezzo_unitario_eur::numeric,
       CASE WHEN disponibilita ~ '^\d+$' THEN disponibilita::int END,   -- 'da planimetria' = NULL
       CASE WHEN disponibilita !~ '^\d+$' AND disponibilita IS NOT NULL
            THEN concat_ws('; ', 'disponibilità: ' || disponibilita, note)
            ELSE note END
FROM s_listino;

-- Ragione sociale "normalizzata": minuscolo, senza forma societaria, senza punteggiatura
-- es. 'ZENIT STUDIOS S.P.A.' e 'Zenit Studios S.p.A.' -> 'zenit studios'
CREATE FUNCTION pg_temp.norm(nome text) RETURNS text LANGUAGE sql IMMUTABLE AS $$
    SELECT trim(regexp_replace(
               regexp_replace(lower(nome),
                   '(^|[^a-z])(s\.?r\.?l\.?s?|s\.?p\.?a|aps|s\.?n\.?c|s\.?a\.?s)\.?(?=[^a-z]|$)', '\1 ', 'g'),
               '[^a-z0-9]+', ' ', 'g'))
$$;

-- Contratti senza id_espositore (tutti quelli 2024, anomalia A16): abbinamento per ragione sociale
CREATE TEMP TABLE t_nomi AS
SELECT DISTINCT ragione_sociale AS nome
FROM s_contratti
WHERE nullif(trim(id_espositore), '') IS NULL;

-- 1. nome identico all'anagrafica
INSERT INTO espositore_alias (nome_origine, id_espositore, metodo)
SELECT n.nome, e.id_espositore, 'esatto'
FROM t_nomi n
JOIN espositore e ON e.ragione_sociale = n.nome;

-- 2. nome uguale dopo la normalizzazione (solo se l'abbinamento è unico)
INSERT INTO espositore_alias (nome_origine, id_espositore, metodo)
SELECT n.nome, min(e.id_espositore), 'normalizzato'
FROM t_nomi n
JOIN espositore e ON pg_temp.norm(e.ragione_sociale) = pg_temp.norm(n.nome)
WHERE n.nome NOT IN (SELECT nome_origine FROM espositore_alias)
GROUP BY n.nome
HAVING count(*) = 1;

-- 3. anomalia A17: 'S.r.l.s.' diventato una "s." attaccata all'ultima parola
--    es. 'Bussola Gears.' -> 'Bussola Gear' -> Bussola Gear S.r.l.s.
WITH abbinati AS (
    INSERT INTO espositore_alias (nome_origine, id_espositore, metodo)
    SELECT n.nome, min(e.id_espositore), 'normalizzato'
    FROM t_nomi n
    JOIN espositore e ON pg_temp.norm(e.ragione_sociale) = pg_temp.norm(regexp_replace(n.nome, 's\.$', ''))
    WHERE n.nome NOT IN (SELECT nome_origine FROM espositore_alias)
    GROUP BY n.nome
    HAVING count(*) = 1
    RETURNING nome_origine, id_espositore
)
INSERT INTO anomalia (codice, fonte, riferimento, descrizione, gestione)
SELECT 'A17', 'Contratti', nome_origine,
       'Ragione sociale storpiata, abbinata a ' || id_espositore,
       'Abbinamento con regola specifica (s. finale = S.r.l.s.)'
FROM abbinati;

-- Contratti che restano senza espositore: non si possono caricare
INSERT INTO anomalia (codice, fonte, riferimento, descrizione, gestione)
SELECT 'A16', 'Contratti', c.id_contratto,
       'Espositore non riconosciuto: ' || c.ragione_sociale,
       'Contratto NON caricato, abbinare a mano'
FROM s_contratti c
WHERE nullif(trim(c.id_espositore), '') IS NULL
  AND c.ragione_sociale NOT IN (SELECT nome_origine FROM espositore_alias);

INSERT INTO anomalia (codice, fonte, riferimento, descrizione, gestione)
SELECT 'A16', 'Contratti', edizione,
       count(*) || ' contratti senza id_espositore e partita_iva',
       'Espositore ricavato dalla ragione sociale (tabella espositore_alias)'
FROM s_contratti
WHERE nullif(trim(id_espositore), '') IS NULL
GROUP BY edizione;

INSERT INTO contratto (id_contratto, edizione, id_espositore, codice_stand, stato, data_firma,
                       imponibile_listino, sconto_pct, imponibile, acconto_scadenza, acconto_pagato_il,
                       saldo_scadenza, saldo_pagato_il, rinnovo)
SELECT c.id_contratto, c.edizione::smallint,
       coalesce(nullif(trim(c.id_espositore), ''), a.id_espositore),
       trim(c.codice_stand), 'firmato', c.data_firma::date,
       c.imponibile_listino_eur::numeric, c.sconto_pct::numeric, c.imponibile_eur::numeric,
       c.acconto_scadenza::date, c.acconto_pagato_il::date,
       c.saldo_scadenza::date, c.saldo_pagato_il::date,
       c.rinnovo::boolean
FROM s_contratti c
LEFT JOIN espositore_alias a ON a.nome_origine = c.ragione_sociale
WHERE coalesce(nullif(trim(c.id_espositore), ''), a.id_espositore) IS NOT NULL;

INSERT INTO riga_contratto (id_contratto, riga, codice_voce, descrizione, quantita, prezzo_unitario, importo)
SELECT r.id_contratto, r.riga::smallint, r.codice_voce, r.descrizione,
       r.quantita::numeric, r.prezzo_unitario_eur::numeric, r.importo_eur::numeric
FROM s_righe r
WHERE r.id_contratto IN (SELECT id_contratto FROM contratto);

-- Anomalie dei pagamenti (solo segnalate, i dati non si modificano)
INSERT INTO anomalia (codice, fonte, riferimento, descrizione, gestione)
SELECT 'A19', 'Contratti', id_contratto, 'Scadenza acconto successiva alla scadenza saldo', 'Segnalata'
FROM contratto WHERE acconto_scadenza > saldo_scadenza
UNION ALL
SELECT 'A20', 'Contratti', id_contratto, 'Saldo pagato senza acconto', 'Segnalata, da chiedere al cliente (D11)'
FROM contratto WHERE saldo_pagato_il IS NOT NULL AND acconto_pagato_il IS NULL
UNION ALL
SELECT 'A21', 'Contratti', id_contratto, 'Saldo pagato prima dell''acconto', 'Segnalata'
FROM contratto WHERE saldo_pagato_il < acconto_pagato_il;

-- ---------------------------------------------------------------------
-- Biglietteria
-- ---------------------------------------------------------------------
\echo 'Biglietteria...'

INSERT INTO biglietto (id_biglietto, id_ordine, edizione, acquistato_il, canale, tipo, giorno_valido,
                       prezzo, persone, fascia_eta, provincia, codice_sconto)
SELECT b.id_biglietto, b.id_ordine, b.edizione,
       to_timestamp(b.data_acquisto, 'DD/MM/YYYY HH24:MI'),
       b.canale,
       t.codice,                                                    -- A9: tipo unico tra le edizioni
       CASE WHEN b.giorno_valido = '3 giorni' THEN NULL
            ELSE to_date(b.giorno_valido, 'DD/MM/YYYY') END,
       replace(b.prezzo, ',', '.')::numeric,                        -- A8: decimali con virgola
       b.persone::smallint,
       f.codice,                                                    -- A12, A13: vuoto o 'famiglia' = NULL
       pa.sigla,                                                    -- A10, A11: provincia in sigla
       nullif(trim(b.codice_sconto), '')
FROM s_biglietteria b
JOIN tipo_biglietto_alias t ON t.edizione = b.edizione AND t.nome_origine = b.tipo
LEFT JOIN fascia_eta f ON f.codice = b.fascia_eta
LEFT JOIN provincia_alias pa ON pa.nome_origine = upper(trim(b.provincia));

INSERT INTO anomalia (codice, fonte, riferimento, descrizione, gestione)
SELECT 'A9', 'biglietteria', b.edizione::text,
       count(*) || ' biglietti con tipo non riconosciuto', 'Biglietti NON caricati'
FROM s_biglietteria b
WHERE NOT EXISTS (SELECT 1 FROM tipo_biglietto_alias t WHERE t.edizione = b.edizione AND t.nome_origine = b.tipo)
GROUP BY b.edizione
UNION ALL
SELECT 'A10', 'biglietteria', edizione::text,
       count(*) || ' province scritte per esteso invece che in sigla', 'Convertite in sigla (provincia_alias)'
FROM s_biglietteria
WHERE provincia IS NOT NULL AND upper(trim(provincia)) NOT IN (SELECT sigla FROM provincia)
GROUP BY edizione
UNION ALL
SELECT 'A10', 'biglietteria', edizione::text,
       count(*) || ' province non riconosciute', 'Caricate come NULL'
FROM s_biglietteria
WHERE provincia IS NOT NULL AND upper(trim(provincia)) NOT IN (SELECT nome_origine FROM provincia_alias)
GROUP BY edizione
UNION ALL
SELECT 'A11', 'biglietteria', edizione::text, count(*) || ' biglietti senza provincia', 'NULL = non indicata'
FROM s_biglietteria WHERE provincia IS NULL GROUP BY edizione
UNION ALL
SELECT 'A12', 'biglietteria', edizione::text, count(*) || ' biglietti senza fascia d''età', 'NULL = non indicata'
FROM s_biglietteria WHERE fascia_eta IS NULL GROUP BY edizione
UNION ALL
SELECT 'A13', 'biglietteria', edizione::text, count(*) || ' biglietti con fascia ''famiglia''', 'Non è un''età: NULL'
FROM s_biglietteria WHERE fascia_eta = 'famiglia' GROUP BY edizione
UNION ALL
SELECT 'A14', 'biglietteria', edizione::text,
       count(*) || ' biglietti con codice SCUOLA/STUDENTI senza riduzione di prezzo', 'Codice mantenuto, da chiedere al cliente (D10)'
FROM s_biglietteria WHERE codice_sconto IN ('SCUOLA', 'STUDENTI') GROUP BY edizione;

-- ---------------------------------------------------------------------
-- Tornelli
-- ---------------------------------------------------------------------
\echo 'Tornelli...'

-- 2024: ora locale, varchi 'P1 Nord', esito 1/0 (A2, A3, A4)
INSERT INTO passaggio_varco (edizione, rilevato_il, codice_varco, codice_letto, id_biglietto, esito_ok, anomalia)
SELECT 2024,
       to_timestamp(t.data || ' ' || t.ora, 'DD/MM/YYYY HH24:MI:SS'),
       va.codice, t.codice, b.id_biglietto, t.esito = '1',
       CASE WHEN b.id_biglietto IS NULL THEN 'CODICE_SCONOSCIUTO' END    -- A5
FROM s_tornelli_2024 t
JOIN varco_alias va ON va.nome_origine = t.varco
LEFT JOIN biglietto b ON b.id_biglietto = t.codice;

-- 2025: UTC, varchi 'P1-Nord', esito OK/KO
INSERT INTO passaggio_varco (edizione, rilevato_il, codice_varco, codice_letto, id_biglietto, esito_ok, anomalia)
SELECT 2025,
       t.timestamp_utc::timestamptz,
       va.codice, t.ticket_code, b.id_biglietto, t.result = 'OK',
       CASE WHEN b.id_biglietto IS NULL THEN 'CODICE_SCONOSCIUTO' END
FROM s_tornelli_2025 t
JOIN varco_alias va ON va.nome_origine = t.gate_id
LEFT JOIN biglietto b ON b.id_biglietto = t.ticket_code;

-- A7: doppia lettura = passaggio valido con il passaggio valido precedente dello stesso
-- biglietto allo stesso varco, entro 'doppia_lettura_secondi' (tabella parametro)
WITH validi AS (
    SELECT id, codice_varco, rilevato_il,
           lag(codice_varco) OVER w AS varco_precedente,
           lag(rilevato_il)  OVER w AS ora_precedente
    FROM passaggio_varco
    WHERE esito_ok AND id_biglietto IS NOT NULL
    WINDOW w AS (PARTITION BY id_biglietto ORDER BY rilevato_il)
)
UPDATE passaggio_varco p
SET anomalia = 'DOPPIA_LETTURA'
FROM validi v
WHERE p.id = v.id
  AND v.varco_precedente = v.codice_varco
  AND v.rilevato_il - v.ora_precedente
      < make_interval(secs => (SELECT valore FROM parametro WHERE nome = 'doppia_lettura_secondi')::float8);

INSERT INTO anomalia (codice, fonte, riferimento, descrizione, gestione)
SELECT 'A5', 'tornelli', edizione::text, count(*) || ' passaggi con codice biglietto inesistente', 'Caricati con flag, non contati'
FROM passaggio_varco WHERE anomalia = 'CODICE_SCONOSCIUTO' GROUP BY edizione
UNION ALL
SELECT 'A6', 'tornelli', edizione::text, count(*) || ' passaggi respinti (KO) con biglietto valido', 'Caricati, non contati'
FROM passaggio_varco WHERE NOT esito_ok AND id_biglietto IS NOT NULL GROUP BY edizione
UNION ALL
SELECT 'A7', 'tornelli', edizione::text, count(*) || ' doppie letture', 'Caricate con flag, non contate'
FROM passaggio_varco WHERE anomalia = 'DOPPIA_LETTURA' GROUP BY edizione;

-- ---------------------------------------------------------------------
-- Stand 2025: visite e contatti
-- ---------------------------------------------------------------------
\echo 'Visite e contatti agli stand...'

-- Una riga per stand e per ora (storico aggregato).
-- A26: scansioni prima dell'apertura = valore fuori scala, escluso dai conteggi
INSERT INTO scansione_stand (edizione, codice_stand, rilevato_il, quantita, origine, anomalia)
SELECT 2025, v.codice_stand,
       (v.data || ' ' || v.ora)::timestamp AT TIME ZONE 'Europe/Rome',
       v.scansioni::int, 'storico_orario',
       CASE WHEN v.ora::time < e.ora_apertura THEN 'FUORI_SCALA' END
FROM s_visite v
JOIN edizione e ON e.anno = 2025;

INSERT INTO anomalia (codice, fonte, riferimento, descrizione, gestione)
SELECT 'A26', 'visite_stand', codice_stand || ' ' || to_char(rilevato_il AT TIME ZONE 'Europe/Rome', 'YYYY-MM-DD HH24:MI'),
       quantita || ' scansioni prima dell''apertura', 'Caricata con flag FUORI_SCALA, non contata'
FROM scansione_stand WHERE anomalia = 'FUORI_SCALA';

INSERT INTO contatto_stand (id_contatto, edizione, codice_stand, id_espositore, raccolto_il, email,
                            fascia_eta, provincia, consenso_marketing, interesse)
SELECT k.id_contatto, 2025, k.codice_stand, k.id_espositore,
       k.ts::timestamp AT TIME ZONE 'Europe/Rome',
       k.email, f.codice, pa.sigla,
       coalesce(upper(trim(k.consenso_marketing)) = 'SI', false),      -- A29: vuoto = nessun consenso
       k.interesse
FROM s_contatti k
LEFT JOIN fascia_eta f ON f.codice = k.fascia_eta
LEFT JOIN provincia_alias pa ON pa.nome_origine = upper(trim(k.provincia));

INSERT INTO anomalia (codice, fonte, riferimento, descrizione, gestione)
SELECT 'A28', 'contatti_stand', k.id_contatto, 'Minore con consenso marketing',
       'Email non visibile all''espositore (vista v_contatti_espositore)'
FROM contatto_stand k JOIN fascia_eta f ON f.codice = k.fascia_eta
WHERE f.minorenne AND k.consenso_marketing
UNION ALL
SELECT 'A29', 'contatti_stand', NULL, count(*) || ' contatti senza consenso indicato', 'Consenso = no'
FROM s_contatti WHERE nullif(trim(consenso_marketing), '') IS NULL
HAVING count(*) > 0;

COMMIT;

\echo 'Caricamento completato.'
