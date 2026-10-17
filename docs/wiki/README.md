# Wiki ARCADE Milano

Wiki interna del progetto. Qui teniamo tutto quello che serve per lavorare: cosa c'è da fare, a che punto siamo, cosa abbiamo deciso e perché.

> Regola d'oro: se una cosa è stata decisa, discussa con il cliente o scoperta nei dati, va scritta qui. Quello che non è scritto non esiste.

## Indice

### Il progetto
- [Panoramica del progetto](progetto.md): cliente, obiettivi, utenti, requisiti, criteri di valutazione
- [Team e ruoli](team.md): chi fa cosa tra BID e BAD
- [Glossario](glossario.md): termini e sigle

### Tecnica
- [Architettura](architettura.md): componenti, flussi, punto d'incontro BID/BAD
- [Dati del cliente](dati.md): file ricevuti, struttura, anomalie trovate, numeri di controllo
- [Schema dati](schema-dati.md): tabelle PostgreSQL, diagramma, scelte
- [KPI](kpi.md): definizioni operative degli indicatori

### Gestione del lavoro
- [Programma](programma.md): calendario e milestone
- [Cose da fare](todo.md): attività aperte, in corso, fatte
- [Avanzamento](avanzamento.md): diario del lavoro, aggiornato a ogni sessione
- [Domande per il cliente](domande-cliente.md): dubbi aperti e risposte ricevute

### Decisioni
- [Registro delle decisioni](decisioni/README.md): ogni scelta importante con il suo perché

## Come si usa questa wiki

**La wiki si aggiorna da sola e in automatico ogni volta che il progetto va avanti**: a ogni passo (codice scritto, decisione presa, anomalia trovata, risposta del cliente, attività completata) si aggiornano subito le pagine interessate, senza aspettare che qualcuno lo chieda. In particolare vanno sempre tenuti allineati [avanzamento.md](avanzamento.md), [todo.md](todo.md) e, quando serve, [decisioni/](decisioni/README.md).

1. **Prima di iniziare a lavorare** leggi [avanzamento.md](avanzamento.md) e [todo.md](todo.md).
2. **Quando finisci una sessione** aggiungi una voce in [avanzamento.md](avanzamento.md) e aggiorna [todo.md](todo.md).
3. **Quando prendi una decisione importante** (tecnologia, struttura del DB, definizione di un KPI, gestione di un'anomalia) crea un file in [decisioni/](decisioni/README.md) partendo dal [modello](decisioni/modello.md).
4. **Quando hai un dubbio che solo il cliente può sciogliere** aggiungilo in [domande-cliente.md](domande-cliente.md).

## Convenzioni

- Un argomento per file, nomi in minuscolo con trattini (`nome-file.md`).
- Le date si scrivono `AAAA-MM-GG` (es. `2026-10-17`).
- I link tra pagine sono relativi (`[KPI](kpi.md)`), così funzionano sia in locale sia su GitHub.
- Le decisioni non si cancellano: se cambiano, se ne scrive una nuova che sostituisce la vecchia.
- Nessun dato personale (nomi, email, ecc.) nella wiki, nemmeno come esempio.
