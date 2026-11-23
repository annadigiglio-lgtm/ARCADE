# 0011. Flussi Power Automate dentro la soluzione, solo connettori standard

- **Data:** 2026-11-06
- **Stato:** proposta
- **Chi ha deciso:** BAD

## Contesto

I flussi servono per promemoria di pagamento, conferme, export verso PostgreSQL e rinnovi ([elenco](../../../power-platform/power-automate/README.md)). Un flusso creato fuori da una soluzione non si esporta insieme all'app. Il piano Developer comprende anche i connettori premium, ma in un ambiente di produzione del cliente non ci sarebbero ([decisione 0005](0005-dataverse-sincronizzato-con-postgresql.md)). L'ambiente ha un limite di 750 esecuzioni di flussi al mese.

## Opzioni considerate

- **Flussi personali in "I miei flussi":** semplici; non finiscono nella soluzione e non si possono consegnare.
- **Flussi nella soluzione ARCADE BAD**, con riferimenti di connessione e variabili d'ambiente: si esportano, si importano e si configurano in un ambiente nuovo.

## Decisione

Ogni flusso si crea in ARCADE BAD → Nuovo → Automazione → Flusso cloud. Si usano solo connettori standard (Dataverse, Office 365 Outlook, OneDrive for Business, Operazioni sui dati). Niente HTTP e niente connettori personalizzati. Soglie e destinatari stanno in variabili d'ambiente.

## Perché

- La soluzione esportata contiene app e flussi insieme.
- Un flusso si sposta in un altro ambiente collegando le connessioni, senza riscriverlo.

## Conseguenze

- Dopo un import le connessioni vanno collegate e i flussi accesi a mano.
- I trigger su Dataverse vanno filtrati sulle colonne, per non consumare il limite di esecuzioni.
- Le email agli espositori partono verso indirizzi del team finché il cliente non approva testi e invii.
