# Condividere ARCADE con Docker

Docker avvia API Spring Boot e pagine web in un unico container. PostgreSQL
rimane esterno: per l'ambiente di gruppo la fonte prevista è Supabase.
Non viene creato, ricreato o caricato alcun database da Docker Compose.

Configurazione scelta per il gruppo: **Supabase**. Il file privato
`.env.docker.local` è stato compilato usando la connessione `bid_app` già
presente nel progetto, SSL richiesto e una chiave JWT casuale persistente.
Non sovrascriverlo con il modello di esempio.

Verifica del 2026-11-02: immagine compilata, container avviato e tre login
funzionanti su Supabase. Viste e funzioni API pubblicate tramite SQL Editor;
verificati i quattro endpoint staff, visite e riepilogo espositori e isolamento
tra i due account dal container collegato al database condiviso.

La configurazione privata di questo PC usa la porta **8081**, per affiancare
l'avvio Java sulla 8080. Gli esempi con 8080 sotto si riferiscono al modello
di configurazione: usare la porta indicata da `APP_PORT` nel proprio file.
Per l'accesso da casa vedere [render.md](render.md).

## Scegliere come accedere

| Situazione | Dove gira il container | Indirizzo usato dal gruppo |
|---|---|---|
| Tutti sulla stessa rete | PC di un membro, acceso e con Docker in esecuzione | `http://IP-DEL-PC:8080` |
| Ognuno da casa, unico ambiente | Server raggiungibile dal gruppo, con Docker e accesso HTTPS | URL HTTPS del server |
| Sviluppo individuale | Ogni membro sul proprio PC | `http://localhost:8080` su ogni PC |

Docker prepara l'applicazione; per avere un URL condiviso da reti diverse
serve anche il server che la ospita. Il servizio del gruppo è ora pubblicato su
**https://arcade-milano.onrender.com** (Render Free), con verifica HTTPS completa
di login, dati e ruoli superata. Il PC locale non deve restare acceso per accedervi.

## Avvio su un PC Windows

Servono Docker Desktop avviato, modalità container Linux e Docker Compose.
Eseguire dalla cartella `ARCADE`:

```powershell
if (-not (Test-Path .env.docker.local)) {
    Copy-Item .env.docker.example .env.docker.local
}
```

Compilare `.env.docker.local` con i parametri del database scelto. Non
sovrascrivere un file ambiente già compilato. Per Supabase usare il Session
pooler, il database `postgres`, l'utente `bid_app.CODICE_PROGETTO` e SSL
`require`. Il file `.env` esistente può contenere i parametri del progetto:
trasferirli nel nuovo file senza aggiungerli a Git.

Generare la chiave JWT e incollare il risultato in `ARCADE_JWT_SECRET`:

```powershell
$chiaveArcade = New-Object byte[] 48
$generatoreArcade = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try { $generatoreArcade.GetBytes($chiaveArcade) } finally { $generatoreArcade.Dispose() }
[Convert]::ToBase64String($chiaveArcade)
```

La chiave resta la stessa tra i riavvii. Non è la password degli account.
Se una password contiene `$` o `#`, racchiudere il valore tra apici singoli nel file ambiente.

```powershell
docker compose --env-file .env.docker.local config --quiet
docker compose --env-file .env.docker.local up --build -d
docker compose --env-file .env.docker.local logs --tail 60 app
```

Aprire `http://localhost:8080`. Se la versione avviata tramite Java occupa già
la porta 8080, fermarla con Ctrl+C oppure cambiare `APP_PORT`, per esempio in 8081.
La build compila il progetto ed esegue i test; non richiede Java o Maven installati sul PC.

## Accesso dalla stessa rete

Impostare nel file ambiente:

```dotenv
APP_BIND_ADDRESS=0.0.0.0
```

Ripetere `docker compose --env-file .env.docker.local up -d` per applicare
la modifica. Trovare l'indirizzo IPv4 della scheda Wi-Fi/Ethernet con `ipconfig`.
Gli altri aprono `http://IP-DEL-PC:8080`, per esempio `http://192.168.1.23:8080`.
Dal loro PC `localhost` indica il loro computer, non quello che ospita ARCADE.

Il PC ospitante deve restare acceso. Se l'accesso viene bloccato, verificare
il firewall per la porta scelta e l'eventuale isolamento dei client nella rete
della scuola. Il container ascolta internamente su `0.0.0.0`; la variabile
`APP_BIND_ADDRESS` controlla dove Docker pubblica la porta sul PC.

## Usare il PostgreSQL locale esistente

Su Docker Desktop il database Windows si indica con `host.docker.internal`,
non con `localhost` (che dentro il container indica il container stesso).
Per il database locale di questo progetto i parametri sono:

```dotenv
DB_HOST=host.docker.internal
DB_PORT=5433
DB_NAME=arcade
DB_USER=postgres
DB_PASSWORD='INSERIRE_LA_PASSWORD_DEL_DB_LOCALE'
DB_SSLMODE=disable
```

Questa variante permette di riusare gli account demo locali esistenti.
Se PostgreSQL rifiuta la connessione dal container, verificare le impostazioni
di ascolto e autorizzazione (`listen_addresses`, `pg_hba.conf`); non sono state modificate.
Per il server condiviso usare un account con i soli permessi necessari.

## Account e database condiviso

`staff.demo`, `espositore.demo1` e `espositore.demo2` sono stati creati anche
su Supabase e i tre login dal container sono stati verificati. Il file
`api/demo-accounts.local` non viene copiato nell'immagine.

Gli hash BCrypt e le associazioni a ESP001/ESP002 sono presenti nel DB condiviso.
Lo script `PreparaDemo` esistente
è limitato al DB locale e non va usato contro Supabase.
Il deploy Render fornirà HTTPS. I tre account demo usano le credenziali comuni
concordate, riportate solo nel file privato delle credenziali.

## Aggiornamento e arresto

```powershell
# Dopo modifiche al codice:
docker compose --env-file .env.docker.local up --build -d
# Arresto:
docker compose --env-file .env.docker.local down
```

I dati restano nel PostgreSQL esterno anche quando si arresta il container.
Credenziali, `.env*`, file `*.local` e cache locali sono esclusi dal contesto
di build tramite `.dockerignore`.

## Stato della verifica

Docker Desktop trovato nell'installazione per utente. Build Linux riuscita,
cinque test Java superati, container avviato con limite 512 MB sulla porta 8081.
Pagina/asset, login Supabase, ruoli e rifiuto di token/password errati verificati
con `node api/verifica-condiviso.mjs`.
Superata anche la prova completa dei dati dopo l'aggiornamento delle viste su Supabase.
Il comando `avvia-docker.ps1` individua anche l'installazione per utente e
aggiunge il gestore credenziali Docker al PATH del processo.

Riferimenti: [Docker Compose](https://docs.docker.com/reference/compose-file/services/),
[pubblicazione porte](https://docs.docker.com/engine/network/port-publishing/),
[reti Docker Desktop](https://docs.docker.com/desktop/features/networking/).
