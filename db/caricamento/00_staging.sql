-- =====================================================================
-- Caricamento storico 2024-2025 - passo 0: tabelle di appoggio (staging)
-- Tabelle TEMPORANEE: esistono solo durante la sessione di caricamento.
-- Tutte le colonne sono testo: i dati entrano esattamente come nei file.
-- =====================================================================

SET client_encoding = 'UTF8';
SET TIME ZONE 'Europe/Rome';   -- orari senza fuso nei file = ora italiana (anomalia A2)
SET search_path = arcade;

\echo 'Creazione tabelle di appoggio...'

-- Fogli dell'Excel commerciale (convertiti in CSV da excel_in_csv.py)
CREATE TEMP TABLE s_espositori (
    id_espositore text, ragione_sociale text, partita_iva text, settore text,
    citta text, referente text, email_referente text
);

CREATE TEMP TABLE s_planimetria (
    codice_stand text, padiglione text, nome_padiglione text, mq text,
    posizione text, attivo_dal text
);

CREATE TEMP TABLE s_listino (
    codice text, voce text, unita text, prezzo_unitario_eur text,
    disponibilita text, note text
);

CREATE TEMP TABLE s_contratti (
    id_contratto text, edizione text, id_espositore text, ragione_sociale text,
    partita_iva text, codice_stand text, data_firma text, imponibile_listino_eur text,
    sconto_pct text, imponibile_eur text, acconto_scadenza text, acconto_pagato_il text,
    saldo_scadenza text, saldo_pagato_il text, rinnovo text
);

CREATE TEMP TABLE s_righe (
    id_contratto text, riga text, codice_voce text, descrizione text,
    quantita text, prezzo_unitario_eur text, importo_eur text
);

-- CSV del cliente
CREATE TEMP TABLE s_biglietteria (
    id_ordine text, id_biglietto text, data_acquisto text, canale text, tipo text,
    giorno_valido text, prezzo text, persone text, fascia_eta text, provincia text,
    codice_sconto text,
    edizione smallint            -- non è nel file: si imposta dopo la copia
);

CREATE TEMP TABLE s_tornelli_2024 (data text, ora text, varco text, codice text, esito text);

CREATE TEMP TABLE s_tornelli_2025 (timestamp_utc text, ticket_code text, gate_id text, result text);

CREATE TEMP TABLE s_visite (codice_stand text, data text, ora text, scansioni text);

CREATE TEMP TABLE s_contatti (
    id_contatto text, codice_stand text, id_espositore text, ts text, email text,
    fascia_eta text, provincia text, consenso_marketing text, interesse text
);
