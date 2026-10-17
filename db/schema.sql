-- =====================================================================
-- ARCADE Milano - Schema dati condiviso (PostgreSQL)
-- Stato: BOZZA da discutere con BAD prima del SAL 1 (2026-10-30)
-- Documentazione: docs/wiki/schema-dati.md
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS arcade;
SET search_path = arcade;

-- ---------------------------------------------------------------------
-- Dimensioni
-- ---------------------------------------------------------------------

CREATE TABLE edizione (
    anno            smallint PRIMARY KEY,
    data_inizio     date NOT NULL,
    data_fine       date NOT NULL,
    ora_apertura    time NOT NULL DEFAULT '09:00',
    ora_chiusura    time NOT NULL DEFAULT '19:00',
    CHECK (data_fine >= data_inizio)
);

CREATE TABLE padiglione (
    codice  varchar(2) PRIMARY KEY,          -- P1, P2, P3
    nome    text NOT NULL UNIQUE
);

CREATE TABLE stand (
    codice_stand    varchar(10) PRIMARY KEY, -- es. P1-A01
    padiglione      varchar(2) NOT NULL REFERENCES padiglione,
    mq              numeric(6,1) NOT NULL CHECK (mq > 0),
    posizione       text NOT NULL CHECK (posizione IN ('linea', 'angolo', 'penisola', 'isola')),
    attivo_dal      smallint NOT NULL REFERENCES edizione
);

CREATE TABLE espositore (
    id_espositore   varchar(10) PRIMARY KEY, -- es. ESP001
    ragione_sociale text NOT NULL,
    partita_iva     char(11) NOT NULL UNIQUE CHECK (partita_iva ~ '^[0-9]{11}$'),
    settore         text,
    citta           text,
    referente       text,                    -- dato personale
    email_referente text                     -- dato personale
);

-- Come la ragione sociale e' scritta nelle fonti -> espositore (anomalie A16, A17)
CREATE TABLE espositore_alias (
    nome_origine    text PRIMARY KEY,
    id_espositore   varchar(10) NOT NULL REFERENCES espositore,
    metodo          text NOT NULL CHECK (metodo IN ('esatto', 'normalizzato', 'manuale'))
);

CREATE TABLE voce_listino (
    edizione        smallint NOT NULL REFERENCES edizione,
    codice          varchar(20) NOT NULL,    -- es. SPAZIO-P1, MAGG-ANGOLO, SP-STAGE
    descrizione     text NOT NULL,
    unita           text,
    prezzo_unitario numeric(10,2),
    disponibilita   integer,                 -- NULL = illimitata / da planimetria
    note            text,
    PRIMARY KEY (edizione, codice)
);

-- ---------------------------------------------------------------------
-- Commerciale (alimentato da BAD)
-- ---------------------------------------------------------------------

CREATE TABLE contratto (
    id_contratto        varchar(12) PRIMARY KEY,  -- es. C2025-0001
    edizione            smallint NOT NULL REFERENCES edizione,
    id_espositore       varchar(10) NOT NULL REFERENCES espositore,
    codice_stand        varchar(10) NOT NULL REFERENCES stand,
    stato               text NOT NULL DEFAULT 'firmato'
                        CHECK (stato IN ('preventivo', 'firmato', 'annullato')),
    data_firma          date,
    imponibile_listino  numeric(12,2) NOT NULL CHECK (imponibile_listino >= 0),
    sconto_pct          numeric(5,4) NOT NULL DEFAULT 0 CHECK (sconto_pct BETWEEN 0 AND 1),
    imponibile          numeric(12,2) NOT NULL CHECK (imponibile >= 0),
    acconto_scadenza    date,
    acconto_pagato_il   date,
    saldo_scadenza      date,
    saldo_pagato_il     date,
    rinnovo             boolean NOT NULL DEFAULT false,
    CHECK (stato <> 'firmato' OR data_firma IS NOT NULL)
);

-- Uno stand si vende una sola volta per edizione (contratti non annullati)
CREATE UNIQUE INDEX ux_contratto_stand_edizione
    ON contratto (edizione, codice_stand) WHERE stato <> 'annullato';

CREATE TABLE riga_contratto (
    id_contratto    varchar(12) NOT NULL REFERENCES contratto ON DELETE CASCADE,
    riga            smallint NOT NULL,
    codice_voce     varchar(20) NOT NULL,    -- SPAZIO, MAGG, EX-*, SP-*
    descrizione     text NOT NULL,
    quantita        numeric(10,2) NOT NULL CHECK (quantita > 0),
    prezzo_unitario numeric(12,2) NOT NULL,
    importo         numeric(12,2) NOT NULL,
    PRIMARY KEY (id_contratto, riga)
);

-- ---------------------------------------------------------------------
-- Biglietteria
-- ---------------------------------------------------------------------

CREATE TABLE tipo_biglietto (
    codice      varchar(20) PRIMARY KEY,     -- INTERO, RIDOTTO, ABBONAMENTO_3G, ...
    descrizione text NOT NULL,
    persone     smallint NOT NULL CHECK (persone > 0),
    giorni      smallint NOT NULL CHECK (giorni > 0)
);

-- Nome del tipo nelle fonti, che cambia tra le edizioni (anomalia A9)
CREATE TABLE tipo_biglietto_alias (
    edizione        smallint NOT NULL REFERENCES edizione,
    nome_origine    text NOT NULL,
    codice          varchar(20) NOT NULL REFERENCES tipo_biglietto,
    PRIMARY KEY (edizione, nome_origine)
);

CREATE TABLE provincia (
    sigla   char(2) PRIMARY KEY,
    nome    text NOT NULL UNIQUE
);

-- Provincia scritta come sigla o nome, in maiuscolo (anomalia A10).
-- Il caricamento cerca upper(trim(valore)).
CREATE TABLE provincia_alias (
    nome_origine    text PRIMARY KEY,
    sigla           char(2) NOT NULL REFERENCES provincia
);

CREATE TABLE fascia_eta (
    codice      varchar(10) PRIMARY KEY,     -- 0-7, 8-13, 14-17, 18-24, ...
    minorenne   boolean NOT NULL,
    ordine      smallint NOT NULL
);

CREATE TABLE biglietto (
    id_biglietto    varchar(12) PRIMARY KEY,
    id_ordine       varchar(12) NOT NULL,
    edizione        smallint NOT NULL REFERENCES edizione,
    acquistato_il   timestamptz NOT NULL,
    canale          text NOT NULL CHECK (canale IN ('Online', 'Cassa', 'Rivenditore partner')),
    tipo            varchar(20) NOT NULL REFERENCES tipo_biglietto,
    giorno_valido   date,                    -- NULL = valido tutti i giorni (abbonamento)
    prezzo          numeric(8,2) NOT NULL CHECK (prezzo >= 0),
    persone         smallint NOT NULL CHECK (persone > 0),
    fascia_eta      varchar(10) REFERENCES fascia_eta,   -- NULL = non indicata / famiglia
    provincia       char(2) REFERENCES provincia,        -- NULL = non indicata
    codice_sconto   text
);
CREATE INDEX ix_biglietto_edizione ON biglietto (edizione, giorno_valido);
CREATE INDEX ix_biglietto_acquisto ON biglietto (edizione, acquistato_il);

-- ---------------------------------------------------------------------
-- Varchi (tornelli)
-- ---------------------------------------------------------------------

CREATE TABLE varco (
    codice      varchar(12) PRIMARY KEY,     -- P1-Nord, P1-Sud, P2-Ovest, P3-Est
    padiglione  varchar(2) NOT NULL REFERENCES padiglione
);

-- Nome del varco nelle fonti (anomalia A3)
CREATE TABLE varco_alias (
    nome_origine    text PRIMARY KEY,
    codice          varchar(12) NOT NULL REFERENCES varco
);

CREATE TABLE passaggio_varco (
    id              bigserial PRIMARY KEY,
    edizione        smallint NOT NULL REFERENCES edizione,
    rilevato_il     timestamptz NOT NULL,    -- sempre con fuso (anomalia A2)
    codice_varco    varchar(12) NOT NULL REFERENCES varco,
    codice_letto    varchar(12) NOT NULL,    -- codice come letto dal tornello
    id_biglietto    varchar(12) REFERENCES biglietto,  -- NULL se il codice non esiste
    esito_ok        boolean NOT NULL,
    anomalia        text CHECK (anomalia IN ('CODICE_SCONOSCIUTO', 'DOPPIA_LETTURA')),
    valido          boolean GENERATED ALWAYS AS
                    (esito_ok AND id_biglietto IS NOT NULL AND anomalia IS NULL) STORED
);
CREATE INDEX ix_passaggio_tempo ON passaggio_varco (edizione, rilevato_il);
CREATE INDEX ix_passaggio_biglietto ON passaggio_varco (id_biglietto, rilevato_il);

-- ---------------------------------------------------------------------
-- Stand: scansioni e contatti
-- ---------------------------------------------------------------------

-- Una riga = N scansioni in un istante.
-- Storico 2025: una riga per ora (quantita = scansioni dell'ora).
-- App di scansione BAD (2026): una riga per scansione (quantita = 1).
CREATE TABLE scansione_stand (
    id              bigserial PRIMARY KEY,
    edizione        smallint NOT NULL REFERENCES edizione,
    codice_stand    varchar(10) NOT NULL REFERENCES stand,
    rilevato_il     timestamptz NOT NULL,
    quantita        integer NOT NULL DEFAULT 1 CHECK (quantita >= 0),
    origine         text NOT NULL CHECK (origine IN ('storico_orario', 'app')),
    anomalia        text CHECK (anomalia IN ('FUORI_SCALA'))
);
CREATE INDEX ix_scansione_stand ON scansione_stand (edizione, codice_stand, rilevato_il);

CREATE TABLE contatto_stand (
    id_contatto         varchar(12) PRIMARY KEY,
    edizione            smallint NOT NULL REFERENCES edizione,
    codice_stand        varchar(10) NOT NULL REFERENCES stand,
    id_espositore       varchar(10) NOT NULL REFERENCES espositore,
    raccolto_il         timestamptz NOT NULL,
    email               text,                -- dato personale
    fascia_eta          varchar(10) REFERENCES fascia_eta,
    provincia           char(2) REFERENCES provincia,
    consenso_marketing  boolean NOT NULL DEFAULT false,  -- vuoto = nessun consenso (A29)
    interesse           text
);
CREATE INDEX ix_contatto_espositore ON contatto_stand (id_espositore, edizione);

-- ---------------------------------------------------------------------
-- Qualita' dei dati e utenti
-- ---------------------------------------------------------------------

-- Registro delle anomalie trovate durante il caricamento (codici di docs/wiki/dati.md)
CREATE TABLE anomalia (
    id              bigserial PRIMARY KEY,
    codice          varchar(4) NOT NULL,     -- A1 ... A31
    fonte           text NOT NULL,           -- file o tabella
    riferimento     text,                    -- chiave della riga coinvolta
    descrizione     text NOT NULL,
    gestione        text NOT NULL,
    rilevata_il     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE utente (
    id              serial PRIMARY KEY,
    username        text NOT NULL UNIQUE,
    password_hash   text NOT NULL,
    ruolo           text NOT NULL CHECK (ruolo IN ('ADMIN', 'STAFF', 'DIREZIONE', 'ESPOSITORE')),
    id_espositore   varchar(10) REFERENCES espositore,
    -- un espositore e' sempre legato alla sua azienda, gli altri ruoli mai
    CHECK ((ruolo = 'ESPOSITORE') = (id_espositore IS NOT NULL))
);

-- Parametri delle assunzioni usate nei KPI (es. permanenza media)
CREATE TABLE parametro (
    nome        text PRIMARY KEY,
    valore      numeric NOT NULL,
    descrizione text NOT NULL
);
