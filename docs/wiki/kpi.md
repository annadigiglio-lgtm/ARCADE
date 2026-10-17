# KPI

Le definizioni operative **non sono fornite dal cliente**: vanno proposte da noi, concordate con BAD, approvate dal cliente e motivate.
Ogni KPI deve essere calcolato **in un solo posto** (vista SQL nel DB) e usato sia dalle API BID sia da Power BI. Vedi [decisione 0003](decisioni/0003-kpi-in-viste-sql.md).

Stato possibile di ogni KPI: `proposto` → `concordato con BAD` → `approvato dal cliente`.

## Modello per ogni KPI

```
### Nome KPI
- Domanda a cui risponde:
- Definizione:
- Formula:
- Dati usati:
- Assunzioni:
- Vista SQL:
- Dove si vede: (cruscotto / portale / Power BI)
- Stato:
```

## KPI richiesti dalla direzione

### Numero di visitatori
- Domanda a cui risponde: quante persone sono venute alla fiera?
- Definizione: _da decidere_. Opzioni:
  - biglietti venduti (ma un Family vale più persone)
  - persone sui biglietti (somma di `Persone`)
  - ingressi ai tornelli (un abbonato conta più volte)
  - persone distinte entrate almeno una volta
- Nota: il brief distingue **biglietti** (42.600 nel 2025) e **presenze** (54.600). Capire con il cliente come sono calcolate.
- Stato: proposto

### Picco di presenza nei padiglioni
- Domanda a cui risponde: quante persone c'erano al massimo in ogni padiglione, e quando?
- Definizione: _da decidere_. Dipende dal fatto che i tornelli registrino anche le uscite.
- Assunzioni: _da definire_ (es. tempo medio di permanenza se non ci sono uscite)
- Stato: proposto

### Saturazione degli spazi espositivi
- Domanda a cui risponde: quanta parte dello spazio disponibile abbiamo venduto?
- Formula ipotetica: mq venduti / mq disponibili in planimetria per l'edizione (usare `attivo_dal`)
- Stato: proposto

### Ricavo per metro quadrato
- Domanda a cui risponde: quanto rende ogni mq di spazio, per padiglione?
- Formula ipotetica: ricavi / mq. _Da decidere_: ricavi solo spazio o anche extra e sponsor? mq venduti o disponibili?
- Stato: proposto

### Costo per contatto
- Domanda a cui risponde: quanto paga un espositore per ogni contatto raccolto allo stand?
- Formula ipotetica: importo contratto dell'espositore / numero di contatti raccolti
- Dati: contratti 2025 + `contatti_stand_2025` (o `visite_stand_2025`)
- Nota: solo il 2025 ha dati di stand. _Da decidere_: contatti o visite?
- Stato: proposto

## Altri indicatori utili (dalle domande del brief)

- Ricavo per padiglione
- Tasso di rinnovo espositori (tornano / persi)
- Andamento vendite biglietti per giorno
- Affluenza per fascia oraria
- Tasso di conversione biglietti → ingressi
- Confronto 2025 contro 2024 su tutti i KPI
