# Flussi Power Automate

Responsabile: **Adam Nekkouss**. Consultati: Alessandro (dati e app), Anna (export verso PostgreSQL).

Tutti i flussi che costruiamo per ARCADE Milano: perché servono, cosa fanno passo per passo, come si provano. Il cliente non ha dato un elenco di flussi: un flusso è **obbligatorio** quando risolve un problema scritto nel brief o serve a una milestone; gli altri sono **facoltativi** e si fanno solo dopo.

## Regole per tutti i flussi

Riassunto della [decisione 0011](../../docs/wiki/decisioni/0011-flussi-nella-soluzione.md):

- Si creano **dentro la soluzione ARCADE BAD**: make.powerapps.com → Soluzioni → ARCADE BAD → Nuovo → Automazione → Flusso cloud. Un flusso creato in "I miei flussi" non si esporta con la soluzione.
- **Solo connettori standard:** Microsoft Dataverse, Office 365 Outlook, OneDrive for Business, Operazioni sui dati, Pianificazione. Niente HTTP e niente connettori personalizzati.
- **Riferimenti di connessione** (uno per connettore) e **variabili d'ambiente** per soglie e destinatari, così si cambiano senza modificare il flusso.
- **Modalità prova:** finché il cliente non approva testi e invii (domanda D19), le email vanno all'indirizzo del team nella variabile `g5_EmailProva`, non ai referenti.
- **Limite dell'ambiente: 750 esecuzioni al mese** per tutti i flussi insieme. I trigger su Dataverse vanno filtrati sulle colonne che interessano.
- **Nomi:** `ARCADE – FL-0n – Descrizione` (es. `ARCADE – FL-02 – Conferma firma`).
- Ogni flusso ha un ramo "in caso di errore" che avvisa Alessandro.

### Variabili d'ambiente

| Nome | Tipo | Valore iniziale | Usata da |
|---|---|---|---|
| `g5_EmailCommerciale` | testo | indirizzo dell'ufficio commerciale (per la demo: indirizzo del team) | FL-01, 02, 04, 07, 08 |
| `g5_EmailProva` | testo | indirizzo del team | tutti i flussi che scrivono ai referenti |
| `g5_ModalitaProva` | sì/no | sì | tutti |
| `g5_GiorniPreavviso` | numero | 7 | FL-01 |
| `g5_CartellaExport` | testo | percorso OneDrive condiviso con Anna | FL-05 |

### Budget delle esecuzioni (limite 750 al mese)

| Flusso | Frequenza | Esecuzioni al mese |
|---|---|---|
| FL-01 | una volta al giorno | 30 |
| FL-05 | ogni 6 ore + manuale | circa 130 |
| FL-08 | una volta a settimana | 4 |
| FL-02, 03, 04, 06, 07 | uno per contratto o riga, con filtro sulle colonne | qualche decina |
| Prove | — | circa 150 |
| **Totale** | | **meno di 500** |

## Elenco

| ID | Flusso | Avvio | Tipo | Entro |
|---|---|---|---|---|
| FL-01 | Promemoria e solleciti di pagamento | ogni giorno alle 08:00 | **obbligatorio** | 2026-11-18 |
| FL-02 | Conferma di firma del contratto | contratto passa a `firmato` | **obbligatorio** | 2026-11-18 |
| FL-05 | Export dei dati commerciali per PostgreSQL | ogni 6 ore + manuale | **obbligatorio** | 2026-11-18 |
| FL-06 | Invito al rinnovo e prelazione | dall'app (schermata Rinnovi) | **obbligatorio** | 2026-11-19 |
| FL-03 | Invio del preventivo in PDF | dall'app o contratto creato come preventivo | facoltativo | 2026-11-19 |
| FL-04 | Controllo dello stand venduto due volte | contratto creato o modificato | facoltativo | 2026-11-20 |
| FL-07 | Avviso di disponibilità esaurita | riga contratto creata | facoltativo | 2026-11-27 |
| FL-08 | Riepilogo settimanale per la direzione | ogni lunedì | facoltativo | 2026-11-27 |

**Primo flusso da fare: FL-02.** È il più semplice (un trigger e un'email) e serve a preparare connessioni, riferimenti di connessione e variabili d'ambiente nella soluzione. Dopo si esporta la soluzione e gli altri flussi si costruiscono partendo da quello.

## Flussi obbligatori

### FL-01 Promemoria e solleciti di pagamento

**Perché:** nel brief i pagamenti sono "controllati a mano" e i solleciti "partono in ritardo". Nello storico ci sono 121 acconti pagati in ritardo e 8 saldi mai pagati ([dati.md](../../docs/wiki/dati.md), A22–A24).

**Avvio:** Pianificazione, ogni giorno alle 08:00 (fuso Europe/Rome).

**Passi:**
1. Dataverse → *Elenca righe* di `g5_contratto` con filtro: stato `firmato`, edizione dell'anno in corso, acconto o saldo non pagato.
2. Per ogni contratto: acconto = 30% dell'imponibile, saldo = 70%.
3. Classifica ogni rata: **in scadenza** (entro `g5_GiorniPreavviso` giorni), **scaduta**, oppure nessuna azione.
4. Per ogni rata in scadenza o scaduta: email al referente (modello "promemoria" o "sollecito") con numero del contratto, stand, importo e data di scadenza.
5. Un'email di riepilogo all'ufficio commerciale con la tabella di tutte le rate (Operazioni sui dati → Crea tabella HTML).

**Prova:** si firma dall'app un contratto 2026 di prova senza segnarlo pagato → arriva il promemoria dell'acconto. C2026-0200 non genera email, perché è già pagato. I contratti 2024 e 2025 non generano email, perché il filtro prende solo l'edizione in corso.

### FL-02 Conferma di firma del contratto

**Perché:** fase "prima" della demo. Il referente riceve conferma di cosa ha comprato e delle scadenze.

**Avvio:** Dataverse → *Quando una riga viene aggiunta, modificata o eliminata*, tabella `g5_contratto`, modifica, **colonne filtrate `g5_stato`**, condizione `g5_stato = firmato`.

**Passi:**
1. Legge l'espositore (ragione sociale, referente, email) e lo stand.
2. Dataverse → *Elenca righe* di `g5_riga_contratto` del contratto, ordinate per `g5_riga`.
3. Email al referente: stand, righe in tabella, imponibile, acconto 30% con scadenza, saldo 70% con scadenza.
4. Copia all'ufficio commerciale.

**Prova:** si firma un preventivo 2026 dall'app → arriva **una** email (non due) con gli stessi importi dell'app.

### FL-05 Export dei dati commerciali per PostgreSQL

**Perché:** il contratto 2026 venduto dall'app deve arrivare in PostgreSQL per il SAL del 4/12 ([decisione 0005](../../docs/wiki/decisioni/0005-dataverse-sincronizzato-con-postgresql.md), opzione B).

**Avvio:** Pianificazione ogni 6 ore + avvio manuale. Il giorno della demo si può avviare più spesso.

**Passi**, per ogni tabella nell'ordine edizione, padiglione, espositore, stand, voce_listino, contratto, riga_contratto (poi scansione_stand, quando ci sarà):
1. Dataverse → *Elenca righe* con le lookup espanse.
2. Operazioni sui dati → *Seleziona*: rinomina le colonne come in PostgreSQL (si toglie `g5_`) e mette i **codici** al posto dei GUID delle lookup ([mappatura](../../docs/wiki/mappatura-dataverse.md)).
3. Formati del [formato di scambio](../README.md): date `AAAA-MM-GG`, punto decimale, `sconto_pct` come frazione, `rinnovo` true/false.
4. Operazioni sui dati → *Crea tabella CSV*.
5. OneDrive for Business → *Crea file* in `g5_CartellaExport` (sovrascrive).
6. Un file `conteggi.csv` con il numero di righe di ogni tabella.

**Prova:** Anna carica i file senza correzioni a mano; un secondo caricamento non crea duplicati; i conteggi sono uguali a Dataverse.

**Attenzione:** il file `espositore` contiene referenti ed email. La cartella si condivide solo con Anna e non finisce mai su Git.

### FL-06 Invito al rinnovo e prelazione

**Perché:** fase "dopo": "quali espositori tornano e quali perdiamo", invito al rinnovo.

**Avvio:** Power Apps (V2), dal pulsante della schermata Rinnovi, con l'elenco degli espositori scelti.

**Passi:**
1. Per ogni espositore: stand dell'edizione precedente, se è ancora libero, valore del contratto precedente.
2. Email al referente con lo stand dell'anno prima e la scadenza della prelazione (31 marzo).
3. Riepilogo degli inviti all'ufficio commerciale.

**Da decidere:** salvare la data dell'invito richiederebbe una colonna che non è in `schema.sql` (assunzione A15). Per ora non si salva.

## Flussi facoltativi

| ID | Flusso | Cosa fa | Note |
|---|---|---|---|
| FL-03 | Invio del preventivo in PDF | compone il preventivo in HTML, lo salva su OneDrive for Business, lo converte in PDF con *Converti file* e lo manda al referente con Outlook | tutti connettori standard; "Popola un modello Word" sarebbe più comodo ma è premium |
| FL-04 | Stand venduto due volte | se esiste un altro contratto non annullato per lo stesso stand ed edizione, avvisa l'ufficio commerciale | seconda difesa dopo il controllo dell'app |
| FL-07 | Disponibilità esaurita | quando le sponsorizzazioni o gli extra venduti arrivano alla disponibilità del listino, avvisa l'ufficio commerciale | trigger sulle righe con codice `SP-` o `EX-` |
| FL-08 | Riepilogo settimanale | ogni lunedì: stand venduti, imponibile 2026, preventivi aperti, rate in ritardo | per lo stato settimanale al cliente |
| FL-09 | Solleciti a scaglioni | evoluzione di FL-01: 7 giorni prima, giorno della scadenza, +7 giorni, +15 giorni al responsabile | dopo FL-01 |
| FL-10 | Approvazione degli sconti alti | uno sconto oltre il 15% passa dall'approvazione della direzione (connettore Approvazioni) prima della firma | va chiesto al cliente (D17) |
| FL-11 | Preventivo fermo | un preventivo non firmato da 14 giorni manda un promemoria al commerciale | — |
| FL-12 | Avviso di saturazione | avvisa la direzione quando un padiglione supera il 90% dei mq venduti, o se P2 resta sotto il 30% a un mese dalla fiera | P2 nel 2025 era al 28,6% |

## Come si consegna un flusso

1. Costruito e provato nella soluzione, con i nomi e le variabili sopra.
2. Una scheda `FL-0n.md` in questa cartella: avvio, passi, prova fatta ed esito, data.
3. Export della soluzione ([`README_STATO_BAD.md`](../README_STATO_BAD.md#esportare-la-soluzione-aggiornata)): il flusso finisce in `solution/ARCADEBAD/Workflows/`.

Dopo un import in un altro ambiente: si creano le connessioni, si collegano ai riferimenti di connessione e si accendono i flussi, che arrivano spenti.
