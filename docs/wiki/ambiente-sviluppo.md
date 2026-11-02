# Ambiente di sviluppo di Yassin e Daniel

Questa guida descrive l'avvio su **Windows con PowerShell**, usando il repository
esistente e il database condiviso Supabase. Non occorre ricreare il progetto.

## Cosa installare

| Strumento | Yassin: API | Daniel: web |
|---|---|---|
| Git e accesso al repository GitHub | Necessario | Necessario |
| VS Code, oppure l'IDE già usato | Necessario | Necessario |
| Docker Desktop, con container Linux | Per provare il pacchetto completo | Percorso consigliato per l'avvio locale |
| JDK 21 | Consigliato per sviluppo e debug Java sul PC | Facoltativo, se avvia senza Docker |
| Extension Pack for Java in VS Code | Consigliato | Facoltativo |
| Maven | Serve per l'avvio Java; disponibile anche tramite lo script del progetto | Facoltativo |
| Node.js | Facoltativo, per gli script di verifica HTTP | Facoltativo, per gli script di verifica HTTP |

Docker costruisce l'app usando Java e Maven dentro il container: per quell'avvio
non serve installarli sul PC. Per modificare HTML, CSS e JavaScript bastano gli
strumenti integrati di VS Code; il frontend attuale non richiede `npm install`.
Non occorre installare PostgreSQL per collegarsi al Supabase già predisposto.

Installazione Docker: seguire la [guida ufficiale Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
configurando WSL 2 se richiesto. Aprire Docker Desktop e attendere che il motore
sia pronto. Per Java in VS Code usare l'[Extension Pack for Java](https://code.visualstudio.com/docs/java/extensions).
Installare un **JDK 21**, non soltanto un JRE; ad esempio dal
[download Microsoft OpenJDK](https://learn.microsoft.com/java/openjdk/download).

## 1. Scaricare il repository

Da una cartella dove tenere il progetto:

```powershell
git clone https://github.com/annadigiglio-lgtm/ARCADE.git
cd ARCADE
code .
```

Se GitHub nega l'accesso, Anna deve verificare che l'account del membro sia
autorizzato al repository. Se il repository è già clonato, aprire quella copia
senza clonarne una seconda. I comandi successivi partono dalla cartella `ARCADE`.

## 2. Ricevere i parametri privati da Anna

I file con credenziali non arrivano con `git clone`, perché sono ignorati da Git.
Chiedere ad Anna, tramite un canale privato:

- Host del Session pooler Supabase, username `bid_app.<PROJECT-REF>` e password DB.
- Username e password dei tre account demo dell'app.
- Per gli script di verifica, il file `api/demo-accounts.local`, oppure i valori
  da riportare nel medesimo formato `username=password`.

La password del database e quella usata nella pagina di login sono diverse.
Per eseguire l'app non serve accedere al pannello Render o avere il ruolo
amministratore Supabase. Tutte le copie collegate a Supabase leggono gli stessi
dati: eventuali scritture sul DB riguardano anche gli altri e il sito online.

## 3. Avviare con Docker: percorso comune

Una sola volta, se il file privato non esiste:

```powershell
Copy-Item .env.docker.example .env.docker.local
```

Compilare `.env.docker.local` usando i valori ricevuti da Anna:

| Parametro | Valore |
|---|---|
| `APP_BIND_ADDRESS` | `127.0.0.1` |
| `APP_PORT` | `8081`, per usare gli stessi comandi di verifica del progetto |
| `DB_HOST` | Host del Session pooler ricevuto da Anna |
| `DB_PORT` | `5432` |
| `DB_NAME` | `postgres` |
| `DB_USER` | Username completo ricevuto da Anna |
| `DB_PASSWORD` | Password del DB ricevuta da Anna |
| `DB_SSLMODE` | `require` |
| `ARCADE_JWT_SECRET` | Una chiave casuale generata sul proprio PC |
| `ARCADE_DEMO_ISTANTE` | Lasciare il valore del modello per la demo storica |

Per generare la propria chiave JWT, eseguire e copiare il risultato nel file:

```powershell
$chiaveSviluppo = New-Object byte[] 48
$generatoreSviluppo = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try { $generatoreSviluppo.GetBytes($chiaveSviluppo) } finally { $generatoreSviluppo.Dispose() }
[Convert]::ToBase64String($chiaveSviluppo)
```

Non occorre ricevere o copiare la chiave JWT di Render. La chiave locale può
essere diversa per ciascun PC. Non sovrascrivere file ambiente già compilati.

Con Docker Desktop aperto:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File avvia-docker.ps1
```

La prima build scarica Java, Maven e dipendenze; richiede Internet. Lo script
compila, esegue i test e avvia il container. Aprire **http://localhost:8081**.
Accedere con le credenziali applicative ricevute da Anna.
Gli utenti su Supabase sono già presenti: non eseguire `PreparaDemo` o gli
script di creazione/caricamento del DB per questo avvio.

Comandi utili:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File avvia-docker.ps1 -Azione stato
powershell -NoProfile -ExecutionPolicy Bypass -File avvia-docker.ps1 -Azione log
powershell -NoProfile -ExecutionPolicy Bypass -File avvia-docker.ps1 -Azione ferma
```

## 4. Yassin: lavorare sulle API

Aprire `api/pom.xml` e lasciare che l'IDE importi il progetto Maven. Il codice è
in `api/src/main/java/it/arcade/`, i test in `api/src/test/` e il contratto HTTP
in `api/openapi.yaml`. Se l'IDE non rileva il progetto, aprire la cartella `api`
come progetto Maven. Gli endpoint e il contratto devono restare allineati.

Può usare l'avvio Docker sopra. Per sviluppare con il debugger Java direttamente
sul PC, installare JDK 21 e verificare `java -version` e `javac -version`.
Se Maven manca, dalla radice del repository:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File api/prepara-maven.ps1
```

Creare nella radice `.env.sviluppo.local` con i parametri Supabase ricevuti:

```dotenv
DB_HOST=INSERIRE_HOST_SESSION_POOLER
DB_PORT=5432
DB_NAME=postgres
DB_USER=INSERIRE_USERNAME_COMPLETO
DB_PASSWORD=INSERIRE_PASSWORD_DB
DB_SSLMODE=require
```

In questo file usare valori senza apici esterni oppure tra doppi apici: lo
script Java non legge gli apici singoli di Compose. Non passare direttamente
`.env.docker.local` allo script Java. La chiave JWT viene generata dallo script.

```powershell
# Compila, esegue i test e avvia su http://localhost:8080.
powershell -NoProfile -ExecutionPolicy Bypass -File api/avvia.ps1 -FileEnv .env.sviluppo.local

# Solo compilazione e test, senza avviare il server:
powershell -NoProfile -ExecutionPolicy Bypass -File api/avvia.ps1 -FileEnv .env.sviluppo.local -SoloCompila
```

Per il debug tramite IDE impostare le stesse variabili DB e una chiave
`ARCADE_JWT_SECRET` di almeno 32 byte nella configurazione locale di esecuzione,
poi avviare in debug `it.arcade.ArcadeApplication`. Le estensioni Java forniscono
il supporto [run/debug/test](https://code.visualstudio.com/docs/java/extensions).
Le impostazioni private dell'IDE non vanno versionate.

## 5. Daniel: lavorare sulle pagine

I file attuali sono `web/index.html`, `web/style.css` e `web/app.js`. Il frontend
è HTML/CSS/JavaScript, servito dall'app Spring Boot sulla stessa origine delle API.
Per questo percorso non serve un secondo server frontend o una configurazione CORS.

Avviare con Docker come al punto 3. Dopo modifiche ai file di `web/`, salvare e
rieseguire `avvia-docker.ps1`: le pagine sono copiate nel pacchetto durante la
build e il solo ricaricamento del browser non aggiorna il container.
Poi ricaricare http://localhost:8081, eventualmente con Ctrl+F5.

Se Daniel sceglie l'avvio Java, usare il punto 4: fermare il server con Ctrl+C e
rieseguire il comando senza `-SenzaCompilare`, quindi aprire localhost:8080.
Aprire `index.html` con doppio clic o con Live Server, senza configurare le API,
non riproduce l'avvio previsto: le richieste usano percorsi come `/auth/login`.

## 6. Verificare e condividere il lavoro

Prima verificare dal browser login staff, dati dei padiglioni e i due account
espositori. Con Node.js e il file privato `api/demo-accounts.local` è disponibile
anche la verifica HTTP, che non modifica i dati:

```powershell
node api/verifica-condiviso.mjs http://127.0.0.1:8081
# Per l'avvio Java, usare invece http://127.0.0.1:8080.
```

Lavorare su un proprio branch, ad esempio `feat/api-riepilogo` o
`feat/portale-riepilogo`, e aprire una pull request per la revisione del gruppo.
Modificare il codice locale non cambia il sito pubblico. Per aggiornare Render
il codice deve arrivare nel branch `main` e va avviato un deploy manuale.
Coordinarsi con Anna per la pubblicazione; vedere [render.md](render.md).

Non ripubblicare le viste SQL e non ricreare lo storico per ogni avvio. Le
modifiche allo schema si provano nel database locale separato e si coordinano
con Anna prima di applicarle a Supabase. Per questa attività aggiuntiva servono
PostgreSQL, i dati e le istruzioni della [guida caricamento](guida-caricamento.md).

## Se qualcosa non funziona

| Problema | Controllo |
|---|---|
| Docker non trovato o motore non disponibile | Aprire Docker Desktop, attendere l'avvio e riaprire il terminale dopo l'installazione |
| Porta occupata | Cambiare `APP_PORT` e usare quella porta nel browser e nella verifica |
| Modifiche web non visibili | Ricostruire il container, poi Ctrl+F5; per Java ricompilare e riavviare |
| Login o dati non disponibili | Leggere i log; verificare parametri DB, connessione Internet e credenziali applicative |
| File privati mancanti dopo il clone | Riceverli da Anna; non sono inclusi in Git |
| Sito online diverso da quello locale | Il deploy Render va eseguito dopo l'aggiornamento di `main` |
