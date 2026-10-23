# 0005. Dati commerciali su Dataverse, sincronizzati verso PostgreSQL

- **Data:** 2026-10-23
- **Stato:** accettata (modalità di sincronizzazione da definire)
- **Chi ha deciso:** BID + BAD

## Contesto

BAD non ha licenze Power Apps premium: i connettori PostgreSQL, i connettori personalizzati verso una REST API e l'azione HTTP di Power Automate non sono disponibili. Power Apps quindi non può scrivere direttamente nel database PostgreSQL condiviso né chiamare le API BID.
BAD può invece creare un ambiente Power Platform dedicato al progetto e lavorare su Dataverse.

## Opzioni considerate

- **Power Apps scrive su PostgreSQL** (direttamente o tramite le API BID): richiede connettori premium, non disponibile.
- **Due basi dati separate senza collegamento**: i numeri non tornerebbero tra le viste.
- **Dataverse per il back-office, sincronizzato verso PostgreSQL**: BAD lavora con gli strumenti che ha, PostgreSQL resta il punto d'incontro per l'analisi.

## Decisione

- BAD crea un ambiente Power Platform per il progetto e gestisce in **Dataverse** espositori, planimetria, listino, contratti, acconti e prelazione.
- I dati commerciali vengono **copiati in PostgreSQL** con una sincronizzazione a senso unico (Dataverse → PostgreSQL).
- **Power BI legge PostgreSQL**, come le API BID: i KPI restano calcolati una sola volta nelle viste SQL ([decisione 0003](0003-kpi-in-viste-sql.md)).

## Perché

- È l'unica strada che non richiede licenze premium.
- PostgreSQL resta l'unica fonte per tutte le viste: i numeri tornano tra Power BI, cruscotto e portale.

## Conseguenze

- **Dataverse è la fonte di verità per i dati commerciali**: in PostgreSQL le tabelle commerciali (`espositore`, `stand`, `voce_listino`, `contratto`, `riga_contratto`) si aggiornano solo con la sincronizzazione, mai a mano o dalle API BID.
- Va definita una **mappatura** tra colonne Dataverse e tabelle PostgreSQL, condivisa tra i due team.
- I codici di business (es. `id_contratto` `C2026-0001`, `id_espositore`) vanno generati in Dataverse e copiati così come sono.
- I dati commerciali sono allineati con un ritardo che dipende dalla sincronizzazione scelta.
- Lo storico 2024-2025 entra una sola volta, per un'unica strada (vedi punti aperti), per evitare due pulizie diverse dello stesso Excel.

## Punti aperti

- [ ] **Chi fa la sincronizzazione e come** (opzioni in [architettura.md](../architettura.md#sincronizzazione-dataverse--postgresql))
- [ ] **Storico 2024-2025**: proposta di passare i dati commerciali già puliti da BID (abbinamenti di A16-A17) a BAD per l'importazione in Dataverse, così storico e nuovi contratti seguono la stessa strada
- [ ] Verificare se in quell'ambiente Dataverse è disponibile senza licenza premium: in generale l'uso di Dataverse in Power Apps è legato alle stesse licenze
