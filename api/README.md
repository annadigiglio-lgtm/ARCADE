# API e prima demo locale

Percorso implementato: login → cruscotto staff e login → visite del proprio stand.
Java 21, Spring Boot 3.5, JDBC e PostgreSQL; la pagina web viene servita dalla stessa
applicazione, senza richiedere un secondo server o configurazione CORS.

## Avvio da PowerShell

Aprire un terminale nella cartella `ARCADE`. Servono Java 21 e il database locale già
caricato con gli script esistenti. Questi comandi **non ricreano il database**.

```powershell
# Solo se Maven non è installato e manca .tools/apache-maven-3.9.9:
powershell -NoProfile -ExecutionPolicy Bypass -File api/prepara-maven.ps1

# Una sola volta: crea uno staff e due espositori nel DB locale esistente.
powershell -NoProfile -ExecutionPolicy Bypass -File api/avvia.ps1 -PreparaDemo

# Avvio normale: compila, esegue i test e avvia l'applicazione.
powershell -NoProfile -ExecutionPolicy Bypass -File api/avvia.ps1
```

Aprire **http://localhost:8080**. Le credenziali generate si trovano in
`api/demo-accounts.local`, escluso da Git. Username: `staff.demo`,
`espositore.demo1`, `espositore.demo2`. La creazione rifiuta di sovrascrivere
il file o account esistenti; non rieseguirla dopo che è riuscita.

Gli utenti espositori sono associati ai primi due espositori con visite 2025.
Le password sono casuali; nel DB vengono salvate soltanto come hash BCrypt.
Il token dura un'ora ed è conservato nella memoria della pagina: ricaricare
la pagina richiede un nuovo login.

## Configurazione

`avvia.ps1` legge `.env.local` dalla radice, con i campi di `.env.local.example`.
La connessione imposta `currentSchema=arcade`, necessario alle funzioni SQL.
Per il solo sviluppo locale viene riusata la connessione di prova già presente.
Per un ambiente condiviso usare un account con permessi di sola lettura, come
`bid_app`, invece dell'amministratore, e impostare una chiave JWT persistente.

Variabili facoltative:

| Variabile | Default | Significato |
|---|---|---|
| `ARCADE_JWT_SECRET` | casuale a ogni avvio dello script | Almeno 32 byte; non versionare |
| `ARCADE_DEMO_ISTANTE` | `2025-12-20T11:55:00+01:00` | Istante fisso della demo; `live` usa l'ora reale |
| `PORT` | `8080` | Porta HTTP |
| `SERVER_ADDRESS` | `127.0.0.1` | Interfaccia di ascolto locale |

In demo i dati sono storici reali riferiti all'istante configurato. Il polling
ogni 30 secondi rilegge i dati, ma **non fa avanzare l'orologio**. Non ci sono
ancora una simulazione in movimento o avvisi di capienza.

## Endpoint implementati

- `POST /auth/login`
- `GET /affluenza/padiglioni` (STAFF)
- `GET /affluenza/andamento` (STAFF)
- `GET /affluenza/ingressi` (STAFF)
- `GET /affluenza/giornata` (STAFF)
- `GET /espositore/me/visite?edizione=2025` (ESPOSITORE)
- `GET /espositore/me/riepilogo?edizione=2025` (ESPOSITORE)

La pagina staff mostra presenze, visitatori, ingressi, picco, grafico andamento
e ingressi orari. Il grafico ha anche una tabella testuale espandibile. Il portale mostra
le visite per giorno e ora e permette di scegliere l'edizione. Nel 2024 le
visite non erano rilevate: l'assenza di righe non significa zero visite.

L'identificativo espositore viene ricavato dal JWT firmato; un parametro URL
`idEspositore` non modifica il filtro. Nessun endpoint implementato restituisce
nomi o email dei visitatori. Gli errori usano `{status, message}`; un problema
di accesso al database risponde 503 senza dettagli SQL.

## Verifica

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File api/avvia.ps1 -SoloCompila
```

I test automatici verificano credenziali, ruoli, token scaduti, edizioni non
valide e filtri dei due espositori. Usano un DB simulato e non modificano
Supabase. La prova con PostgreSQL reale va eseguita separatamente, accedendo
con i tre account locali e confrontando i dati con le viste SQL.

Con l'applicazione avviata e Node.js disponibile, la verifica HTTP/SQL automatica è:

```powershell
node api/verifica-locale.mjs
```

Controlla i tre login, i quattro endpoint staff, le visite confrontate con SQL,
i ruoli e il tentativo di cambiare espositore tramite URL. Non scrive nel database.
Per riavviare senza ricompilare un pacchetto già aggiornato, aggiungere
`-SenzaCompilare` al comando di avvio.

## Da completare

- Conferma con il team del contratto OpenAPI, ancora indicato come bozza.
- Endpoint contatti, confronto e rinnovo presenti nella specifica, non implementati.
- Export reale da Dataverse e caricamento del contratto commerciale 2026.
- Confronto dei numeri con Power BI e capienze confermate dal cliente.
- Configurazione dell'ambiente condiviso e demo con orologio in movimento.

Riferimenti tecnici: [Spring Boot](https://docs.spring.io/spring-boot/3.5/system-requirements.html)
e [Spring Security JWT](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html).
