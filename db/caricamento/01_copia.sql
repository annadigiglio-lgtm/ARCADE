-- =====================================================================
-- Caricamento storico 2024-2025 - passo 1: copia dei file nelle tabelle di appoggio
-- psql va avviato DALLA CARTELLA DEI DATI del cliente (lo fa carica.ps1).
-- Ogni comando \copy deve stare su una sola riga.
-- =====================================================================

\echo 'Copia dei file...'

\copy s_espositori FROM 'excel_csv/Espositori.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy s_planimetria FROM 'excel_csv/Planimetria.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy s_listino FROM 'excel_csv/Listino_2026.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy s_contratti FROM 'excel_csv/Contratti.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy s_righe FROM 'excel_csv/Righe_contratto.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

\copy s_biglietteria (id_ordine, id_biglietto, data_acquisto, canale, tipo, giorno_valido, prezzo, persone, fascia_eta, provincia, codice_sconto) FROM 'biglietteria_2024.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'UTF8')
UPDATE s_biglietteria SET edizione = 2024 WHERE edizione IS NULL;
\copy s_biglietteria (id_ordine, id_biglietto, data_acquisto, canale, tipo, giorno_valido, prezzo, persone, fascia_eta, provincia, codice_sconto) FROM 'biglietteria_2025.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'UTF8')
UPDATE s_biglietteria SET edizione = 2025 WHERE edizione IS NULL;

-- Formati diversi tra 2024 e 2025 (anomalia A1)
\copy s_tornelli_2024 FROM 'tornelli_2024.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'UTF8')
\copy s_tornelli_2025 FROM 'tornelli_2025.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8')

\copy s_visite FROM 'visite_stand_2025.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy s_contatti FROM 'contatti_stand_2025.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
