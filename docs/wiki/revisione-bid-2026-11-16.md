# Revisione tecnica BID — 16 novembre 2026

## Correzioni

| Problema riscontrato | Correzione |
|---|---|
| Il riepilogo singolo sceglieva il primo stand senza segnalare altri contratti | Nuovo `GET /espositore/me/riepiloghi?edizione=2025`, array ordinato per stand. La pagina mostra tutti i riepiloghi e il costo per contatto dalla vista SQL. |
| Richiesta singola ambigua con più stand | `riepilogo` accetta `codiceStand`; senza selezione, se più stand presenti risponde 409. Con uno stand conserva la risposta precedente. Nessun risultato: 404. |
| Password Unicode potevano superare il limite BCrypt pur rispettando il numero di caratteri | Controllo di 72 byte UTF-8 prima di interrogare il database o eseguire BCrypt; risposta 400 per input troppo lungo. |
| Valori nulli nel picco di giornata non rappresentati nello schema API | `piccoPresenti` nullable nel contratto, come il risultato SQL in assenza di istanti. |
| Possibili risultati parziali in caso di errore di caricamento/rendering | Pulizia dei pannelli nel ramo errore; mai dati precedenti presentati come aggiornati. |
| Errori DB non descritti nella specifica | Risposta 503 comune documentata su tutti gli endpoint, senza dettagli di connessione o record. |

Identità sempre dal JWT, anche nella selezione dello stand. Nessuna aggregazione
di imponibili/contatti tra stand fatta nel browser; i KPI restano definiti in SQL.
Non servono nuove modifiche a Supabase.

## Verifica

- 12 test Java superati: più stand, selezione, risposta vuota, 404/409,
  ruoli e isolamento, login Unicode al limite e oltre il limite,
  errori DB senza divulgazione di dettagli, oltre ai controlli già presenti.
- Test frontend: due stand, NULL distinto da zero, testo inserito in sicurezza,
  pulizia risultati dopo 503, sblocco aggiornamento, logout e vecchie risposte.
- YAML OpenAPI valido, 11 percorsi; nuova prova HTTP su localhost con le viste
  Supabase già disponibili, senza scritture sul database.

## Limiti e attività aperte

- La revisione tecnica non sostituisce la verifica visiva desktop/mobile:
  l'accesso browser assistito non era disponibile nell'ultima prova.
- Questa revisione richiede un nuovo deploy manuale Render; il deploy già
  verificato precedentemente non include automaticamente queste correzioni.
- Export commerciali e scansioni reali BAD ancora necessari per integrazione 2026.
- Report Power BI, definizioni KPI e condizioni rinnovo da confermare.
- Assenza di dati per un'edizione non equivale a zero attività effettiva.

Non sono state effettuate nuove scritture sul database condiviso.
