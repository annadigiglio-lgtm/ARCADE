-- =====================================================================
-- ARCADE Milano - Dati di base e tabelle di decodifica
-- Stato: BOZZA. Da eseguire dopo schema.sql
-- =====================================================================

SET search_path = arcade;

INSERT INTO edizione (anno, data_inizio, data_fine) VALUES
    (2024, '2024-12-20', '2024-12-22'),
    (2025, '2025-12-19', '2025-12-21'),
    (2026, '2026-12-18', '2026-12-20');   -- date da confermare (domanda D1)

INSERT INTO padiglione (codice, nome) VALUES
    ('P1', 'Console & PC'),
    ('P2', 'Esports & Community'),
    ('P3', 'Indie, Retro & Cosplay');

INSERT INTO varco (codice, padiglione) VALUES
    ('P1-Nord', 'P1'), ('P1-Sud', 'P1'), ('P2-Ovest', 'P2'), ('P3-Est', 'P3');

INSERT INTO varco_alias (nome_origine, codice) VALUES
    ('P1 Nord', 'P1-Nord'), ('P1 Sud', 'P1-Sud'), ('P2 Ovest', 'P2-Ovest'), ('P3 Est', 'P3-Est'),
    ('P1-Nord', 'P1-Nord'), ('P1-Sud', 'P1-Sud'), ('P2-Ovest', 'P2-Ovest'), ('P3-Est', 'P3-Est');

INSERT INTO tipo_biglietto (codice, descrizione, persone, giorni) VALUES
    ('INTERO',          'Giornaliero intero',             1, 1),
    ('RIDOTTO',         'Giornaliero ridotto',            1, 1),
    ('ABBONAMENTO_3G',  'Abbonamento 3 giorni',           1, 3),
    ('FAMILY',          'Family 2 adulti + 2 ragazzi',    4, 1),
    ('OMAGGIO_U8',      'Gratuito under 8',               1, 1),
    ('BUSINESS',        'Business Day (venerdi mattina)', 1, 1),
    ('VIP',             'VIP Experience',                 1, 1),
    ('STAMPA',          'Accredito stampa',               1, 1);

INSERT INTO tipo_biglietto_alias (edizione, nome_origine, codice) VALUES
    (2024, 'Intero',      'INTERO'),
    (2024, 'Ridotto',     'RIDOTTO'),
    (2024, 'Abb. 3gg',    'ABBONAMENTO_3G'),
    (2024, 'Family',      'FAMILY'),
    (2024, 'Omaggio U8',  'OMAGGIO_U8'),
    (2024, 'Business',    'BUSINESS'),
    (2024, 'VIP',         'VIP'),
    (2024, 'Stampa',      'STAMPA'),
    (2025, 'Giornaliero intero',             'INTERO'),
    (2025, 'Giornaliero ridotto 8-14 anni',  'RIDOTTO'),
    (2025, 'Abbonamento 3 giorni',           'ABBONAMENTO_3G'),
    (2025, 'Family 2 adulti + 2 ragazzi',    'FAMILY'),
    (2025, 'Gratuito under 8',               'OMAGGIO_U8'),
    (2025, 'Business Day (venerdì mattina)', 'BUSINESS'),
    (2025, 'VIP Experience',                 'VIP'),
    (2025, 'Accredito stampa',               'STAMPA');

INSERT INTO fascia_eta (codice, minorenne, ordine) VALUES
    ('0-7', true, 1), ('8-13', true, 2), ('14-17', true, 3),
    ('18-24', false, 4), ('25-34', false, 5), ('35-44', false, 6), ('45+', false, 7);

INSERT INTO provincia (sigla, nome) VALUES
    ('BG', 'Bergamo'), ('BO', 'Bologna'), ('BS', 'Brescia'), ('CO', 'Como'),
    ('CR', 'Cremona'), ('FI', 'Firenze'), ('GE', 'Genova'), ('LC', 'Lecco'),
    ('LO', 'Lodi'), ('MB', 'Monza e Brianza'), ('MI', 'Milano'), ('NA', 'Napoli'),
    ('NO', 'Novara'), ('PC', 'Piacenza'), ('PD', 'Padova'), ('PR', 'Parma'),
    ('PV', 'Pavia'), ('RM', 'Roma'), ('TO', 'Torino'), ('VA', 'Varese'), ('VR', 'Verona');

-- Ogni provincia si riconosce sia dalla sigla sia dal nome in maiuscolo
INSERT INTO provincia_alias (nome_origine, sigla)
    SELECT sigla, sigla FROM provincia
    UNION
    SELECT upper(nome), sigla FROM provincia;

INSERT INTO parametro (nome, valore, descrizione) VALUES
    ('permanenza_minuti', 120,
     'Minuti di permanenza stimati dopo l''ultimo passaggio della giornata (i varchi non registrano le uscite)'),
    ('doppia_lettura_secondi', 120,
     'Due letture dello stesso biglietto allo stesso varco entro questo intervallo contano come una');
