# Pubblicazione gratuita: Docker su Render + Supabase

## Stato

- Immagine Docker compilata e cinque test Java superati dentro il container Linux.
- Container locale avviato con limite 512 MB su `http://localhost:8081`.
- Connessione Supabase, tre login, ruoli e rifiuto delle credenziali errate verificati.
- Account `staff.demo`, `espositore.demo1`, `espositore.demo2` creati su Supabase;
  stesse credenziali del file privato `api/demo-accounts.local`.
- Viste/funzioni API pubblicate dall'utente tramite SQL Editor; verifica completa
  dal container superata per i quattro endpoint staff, visite e riepilogo espositori.
- Blueprint `render.yaml` preparato; **nessun servizio Render è stato creato**.

## 1. Completare le viste su Supabase

**Completato il 2026-11-02.** I passaggi sotto restano come istruzioni per
eventuali aggiornamenti futuri. Il controllo completo è già stato eseguito con esito positivo.

L'account `bid_app` non ha CREATE sullo schema e non è proprietario delle viste
esistenti. Non può eseguire questo aggiornamento. Usare il collegamento Supabase
con accesso amministrativo, oppure il pannello del progetto:

1. Aprire SQL Editor e una nuova query; selezionare il ruolo proprietario `postgres`.
2. Incollare tutto `db/pubblica_api_supabase.sql` ed eseguire.
3. L'ultima query deve restituire tre righe, una per padiglione.

Il file aggiorna le viste KPI e API in una transazione; non ricrea le tabelle,
non ricarica lo storico e non cancella dati. È generato dai due script SQL già
provati in locale. La prova di aggiornamento locale è stata eseguita con rollback.
Se gli script sorgente cambiano, rigenerare il file con:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File db/prepara_pubblicazione_supabase.ps1
```

Con Docker avviato verificare tutti gli endpoint:

```powershell
node api/verifica-condiviso.mjs
```

Prima dell'aggiornamento SQL funziona solo la verifica `--solo-login`; i dati del
cruscotto e del portale richiedono le viste mancanti.

## 2. Pubblicare il codice nel repository

Il repository Git configurato è `annadigiglio-lgtm/ARCADE`. I nuovi file Docker,
`render.yaml`, script e documentazione devono essere inclusi nel branch scelto
per Render. Nessun push o commit è stato eseguito automaticamente.

I file `.env`, `.env.docker.local` e `api/demo-accounts.local` sono privati e
ignorati da Git; non includerli nel repository o nell'immagine.

## 3. Creare il servizio Render Free

Con il collegamento Render autorizzato si può procedere dal servizio connesso.
In alternativa, sul pannello Render:

1. Usare un account/workspace gratuito e collegare il repository GitHub del progetto.
2. Creare un **Blueprint** dal repository, indicando `render.yaml`.
3. Verificare che il solo servizio sia `arcade-milano`, tipo web, runtime Docker,
   regione Frankfurt e piano **Free**. Non sono definiti database Render o dischi.
4. Inserire `DB_HOST`, `DB_USER` e `DB_PASSWORD`, prendendoli dal file privato
   `.env.docker.local` senza aggiungere gli apici esterni usati nel file dotenv.
   La chiave JWT viene generata da Render; gli altri parametri sono già nel Blueprint.
5. Confermare solo risorse gratuite e avviare il deploy.

Il repository ARCADE ha il Dockerfile nella radice: mantenere contesto `.` e
percorso `./Dockerfile`. Render costruisce il Dockerfile direttamente; non usa
`compose.yaml`. Non serve Docker installato sui PC che visitano il sito.

Se si usa **New → Web Service** invece del Blueprint, riportare manualmente le
variabili e impostazioni di `render.yaml`, inclusi runtime Docker, piano Free,
`SERVER_ADDRESS=0.0.0.0` e porta `10000`.

## 4. Controllare l'URL

Render assegna un URL HTTPS `https://<nome-assegnato>.onrender.com`; usare quello
restituito dal deploy, senza supporre che `arcade-milano` sia disponibile.

```powershell
node api/verifica-condiviso.mjs https://NOME-ASSEGNATO.onrender.com
```

Il controllo legge le credenziali locali e non stampa password o token. Dopo
la verifica provare nel browser cruscotto e due account espositori. Il controllo
di salute su `/` verifica il server web, non la disponibilità delle viste DB.

## Costi e limiti

Il Blueprint imposta `plan: free`, non crea altre risorse e disabilita i deploy
automatici da commit (`autoDeployTrigger: off`). Le build successive sono manuali.
La memoria JVM è limitata per lasciare spazio alle componenti native nel piano
da 512 MB; la stessa configurazione viene usata nella prova Docker locale.

Il piano gratuito sospende l'app dopo 15 minuti senza richieste; una visita la
riattiva e può richiedere circa un minuto. Aprire il link prima della demo.
Ci sono quote mensili per ore, traffico e build, e limiti per traffico elevato
verso servizi esterni. Non aggiungere risorse a pagamento per superarle.
Senza metodo di pagamento, esaurire le quote può sospendere il servizio o le build.
Controllare comunque il piano e le condizioni mostrate durante la creazione.

Riferimenti ufficiali: [piano gratuito](https://render.com/docs/free),
[Docker](https://render.com/docs/docker),
[Blueprint](https://render.com/docs/blueprint-spec).
