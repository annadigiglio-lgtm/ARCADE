# 0002. PostgreSQL condiviso come punto d'incontro BID/BAD

- **Data:** 2026-10-17
- **Stato:** accettata (indicazione del documento di progetto)
- **Chi ha deciso:** documento di progetto, BID

## Contesto

Il documento di progetto dice: "Il punto d'incontro tra i due team è il modello dati: il BID lo progetta e lo alimenta, il BAD porta i dati commerciali e costruisce sopra la BI direzionale."
All'inizio non era chiaro se BID dovesse richiamare le dashboard di BAD tramite API. Non è così: Power BI non espone dati da richiamare, e le interfacce di BID (cruscotto staff, portale espositori) servono utenti diversi da quelli di Power BI (direzione).

## Opzioni considerate

- **Dashboard BAD richiamate da BID:** non praticabile, Power BI non fa da sorgente dati per una web app.
- **Due basi dati separate (Dataverse per BAD, PostgreSQL per BID):** i numeri rischiano di non tornare tra le viste.
- **Un solo PostgreSQL condiviso:** una sola fonte per tutte le interfacce.

## Decisione

Un unico database PostgreSQL, progettato e alimentato da BID. BAD vi porta i dati commerciali e vi collega Power BI. Le interfacce web BID leggono dallo stesso DB tramite le API Spring Boot.

## Perché

- È l'indicazione esplicita del documento di progetto.
- Una sola fonte è il modo più semplice per rispettare il requisito "i numeri devono tornare tra le diverse viste".

## Conseguenze

- Il DB deve essere raggiungibile da tutti e da Power BI: va ospitato in un posto comune (da decidere).
- Va concordato con BAD come entrano nel DB i dati commerciali (API o Power Automate).
- Lo schema è una responsabilità BID e va congelato al SAL 1 (2026-10-30).
