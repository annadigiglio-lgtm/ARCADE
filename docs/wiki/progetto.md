# Panoramica del progetto

Fonti: `Progetto_Laboratorio_Integrato_-_BAD-BID_compilato.pdf` (descrizione del corso) e `ARCADE Milano · Il brief.pdf` (presentazione del cliente al kickoff del 2026-10-16).

## Il cliente

**Factory Studios** organizza **ARCADE Milano**, festival (fittizio) del videogioco e della cultura pop.

- 3 giorni, 3 padiglioni:
  - **P1 Console & PC**: grandi editori e produttori di hardware
  - **P2 Esports & Community**: tornei, palco principale, community
  - **P3 Indie, Retro & Cosplay**: studi indipendenti, collezionismo, artigianato
- Crescita di circa il 20% l'anno

| | 2024 | 2025 |
|---|---|---|
| Espositori | 88 | 110 |
| Biglietti | 35.700 | 42.600 |
| Presenze | 45.700 | 54.600 |
| Ricavi espositori e sponsor | 706k € | 822k € |

**Edizione 2026:** dal 18 al 20 dicembre 2026, 130 stand disponibili, vendite già aperte.
(Il documento del corso dice "fine novembre", il brief "dicembre": vedi [domande-cliente.md](domande-cliente.md).)

Referenti: Paolo Ghirlinzoni, Emanuele Campanini.

## Il problema

La fiera si gestisce con fogli Excel scollegati:
- **Vendita spazi**: listino, mappa stand e contratti in file diversi; extra via email; pagamenti controllati a mano; solleciti in ritardo.
- **Pubblico**: biglietteria e tornelli arrivano da fornitori diversi; i numeri si ricostruiscono dopo la fiera e spesso non tornano.
- **Durante la fiera**: lo staff non sa in tempo reale quante persone ci sono in ogni padiglione.
- **Espositori**: chiedono quanta gente è passata dal loro stand e non si sa rispondere, quindi è più difficile convincerli a rinnovare.

## Cosa chiede il cliente

Un'unica piattaforma che faccia due cose:
1. **Vendere meglio**: spazi e sponsorizzazioni dal preventivo al contratto, all'incasso, al rinnovo.
2. **Capire i numeri**: unire biglietti, ingressi e visite agli stand per decidere prima, durante e dopo la fiera.

## Utenti

| Utente | Cosa fa | Interfaccia |
|---|---|---|
| Ufficio commerciale | Vende stand e sponsorizzazioni, segue pagamenti e scadenze | Power Apps (BAD) |
| Direzione | Legge i report e confronta le edizioni | Power BI (BAD) |
| Staff in fiera | Guarda l'affluenza in diretta su uno schermo | Cruscotto web (BID) |
| Espositori | Vedono le visite al proprio stand su una pagina semplice | Portale web (BID) |

## Le domande a cui oggi il cliente non sa rispondere

- Quali padiglioni rendono di più?
- Quali espositori tornano e quali perdiamo?
- In quali giorni il pubblico compra i biglietti?
- A che ora i padiglioni sono più pieni?
- Quanti biglietti venduti diventano ingressi?
- Come va il 2025 rispetto al 2024?

## KPI richiesti dalla direzione

- Numero di visitatori e picco di presenza nei padiglioni
- Saturazione degli spazi espositivi e ricavo per metro quadrato
- Costo per contatto generato presso gli stand

Le definizioni **non sono date**: vanno concordate con il cliente e motivate. Vedi [kpi.md](kpi.md).

## Obiettivo minimo: le tre fasi della fiera

- **Prima**: vendita di uno stand, dal preventivo al contratto
- **Durante**: affluenza nei padiglioni e visite agli stand in tempo reale
- **Dopo**: riepilogo all'espositore, confronto tra edizioni, rinnovo

## Requisiti trasversali (valutati dal cliente)

- I numeri devono tornare tra le diverse viste
- Le anomalie dei dati vanno trovate e gestite
- Gli espositori non devono vedere i dati dei concorrenti
- I dati dei minori devono essere tutelati
- I nomi nei dati sono inventati ma vanno trattati come dati personali

## Consegna

Un unico repository Git con: piattaforma, processi di caricamento, interfacce web, soluzione Power Platform, schema dati, specifica API, README. Più una presentazione finale con demo dal vivo delle tre fasi.

## Criteri di valutazione

Funzionamento end-to-end, coerenza dei numeri tra le viste, gestione delle anomalie, riservatezza tra espositori, tutela dei minori, qualità del codice, collaborazione tra i team.

L'uso di assistenti AI è ammesso senza limiti, a patto che **chiunque nel team sappia spiegare ogni riga consegnata**.
