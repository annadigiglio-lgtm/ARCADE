# Guida ambiente Power Platform

Come si entra nell'ambiente `ARCADE-Milano-BAD-G5`, con quali permessi, e come si conserva la soluzione nel repository. Lo fa Alessandro, che è amministratore dell'ambiente.

## Requisiti per entrare

- Account della scuola (stessa organizzazione di Microsoft Entra ID dell'ambiente).
- Una licenza Power Apps: va bene il piano Developer gratuito, che si attiva da https://aka.ms/PowerAppsDevPlan con l'account della scuola.
- Nell'ambiente Developer gli utenti **non vengono aggiunti in automatico**: vanno aggiunti a mano.

## Ruoli

Le nostre tabelle `g5_` sono personalizzate e **non sono incluse nel ruolo Basic User**: con il solo Basic User l'app si apre ma non mostra dati. Per questo creiamo due ruoli.

| Ruolo | Come si crea | Per chi |
|---|---|---|
| **ARCADE Lettura** | copia di Basic User + Lettura a livello Organizzazione sulle 7 tabelle `g5_` | BID, Cristian, Yenje |
| **ARCADE Commerciale** | come sopra + Creazione, Scrittura, Accodamento, Accoda a. **Niente Eliminazione**: i contratti si annullano | chi usa il back-office |
| Environment Maker (di sistema) | — | Anna e Yassin, per vedere soluzione, app e flussi |
| System Customizer (di sistema) | — | Lorenzo e Adam, che lavorano dentro la soluzione |

System Administrator resta solo ad Alessandro. Un System Customizer può modificare tabelle e colonne: a BID non serve e romperebbe la sincronizzazione a senso unico.

## Passi

1. admin.powerplatform.microsoft.com → Gestisci → Ambienti → **ARCADE-Milano-BAD-G5** → Impostazioni → Utenti e autorizzazioni.
2. **Ruoli di sicurezza**: creare ARCADE Lettura e ARCADE Commerciale come nella tabella (⋯ → Copia su Basic User, poi la scheda delle tabelle personalizzate).
3. **Utenti** → Aggiungi utente → un utente alla volta → Gestisci ruoli.
4. make.powerapps.com → Soluzioni → ARCADE BAD → Aggiungi esistente → Sicurezza → Ruolo di sicurezza: aggiungere i due ruoli, così si esportano con la soluzione.
5. make.powerapps.com → App → *FUSIONWORK-BACKOFFICE Commerciale* → ⋯ → Condividi: aggiungere gli utenti come utenti, non come co-proprietari.

Nelle app di un ambiente Developer compare un avviso "sviluppo": è normale.

## Problemi noti

| Messaggio | Causa | Cosa fare |
|---|---|---|
| "Graph throttling" all'aggiunta di un utente | troppe richieste a Microsoft Graph in poco tempo (2026-11-04) | aspettare 10–15 minuti, poi un utente alla volta; in alternativa condividere l'app con un ruolo, che aggiunge l'utente all'ambiente |
| L'utente non compare nella ricerca | account di un'altra organizzazione o senza licenza | attivare il piano Developer; se non basta, chiedere al tutor |
| L'app si apre ma è vuota | l'utente ha solo Basic User | assegnare ARCADE Lettura o ARCADE Commerciale |

## Esportare la soluzione

La soluzione si conserva nel repository dopo ogni versione importante (comandi in [`power-platform/README_STATO_BAD.md`](../../power-platform/README_STATO_BAD.md)). Serve anche perché gli ambienti Developer non gestiti vengono sospesi dal 2026-12-15 e cancellati dal 2027-01-15.

## Git e Azure DevOps

| Opzione | Requisiti | Scelta |
|---|---|---|
| Collegamento a Git integrato in Dataverse (Soluzioni → Connetti a Git) | ambiente gestito (Managed Environments), licenze Azure DevOps, ruolo System Administrator | **non possibile**: il piano Developer non comprende gli ambienti gestiti |
| Export con `pac` + commit in questo repository | `pac auth create` con l'account della scuola | **quella che usiamo** |
| Repository su Azure DevOps invece che su GitHub | organizzazione Azure DevOps, gratuita fino a 5 utenti Basic | non serve: codice e servizio Render di BID sono già su GitHub |

Fonte: documentazione Microsoft Learn su Dataverse Git integration e sul piano Developer, consultata il 2026-11-04.
