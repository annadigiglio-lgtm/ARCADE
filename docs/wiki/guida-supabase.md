# Guida: database condiviso su Supabase

Supabase offre PostgreSQL in cloud con un piano gratuito. Lo usiamo come **database condiviso** tra BID e BAD ([decisione 0006](decisioni/0006-supabase.md)). Per lo sviluppo quotidiano ognuno usa PostgreSQL in locale (Docker).

> I limiti del piano gratuito cambiano nel tempo: verificarli su [supabase.com/pricing](https://supabase.com/pricing). A ottobre 2026: 500 MB di database per progetto, 2 progetti attivi per organizzazione, **pausa dopo 7 giorni senza attività**.
> I nostri dati occupano molto meno di 500 MB (circa 200.000 righe).

## 1. Creare il progetto (una persona sola, il responsabile DB)

1. Registrarsi su [supabase.com](https://supabase.com) (anche con l'account GitHub).
2. Creare un'**organizzazione**: nome `ARCADE`, piano **Free**.
3. **New project**:
   - Nome: `arcade-milano`
   - **Database password**: generarne una lunga e salvarla in un gestore di password. **Mai su Git, nella wiki o in chat.**
   - **Region**: una regione europea (es. Central EU - Frankfurt), vicina a Milano e coerente con il GDPR: i dati contengono dati personali.
4. Attendere un paio di minuti che il progetto sia pronto.
5. Annotare la **versione di PostgreSQL** del progetto (nelle impostazioni dell'infrastruttura) e usare la **stessa versione** in Docker.

## 2. Invitare il team

Nelle impostazioni dell'organizzazione → **Team** → invitare per email i membri BID (e, se serve, un referente BAD) per l'accesso al pannello.

Per **collegarsi al database** non serve l'invito: bastano i dati di connessione (punto 3) e un utente del database (punto 5).

## 3. Dati di connessione

Nel pannello del progetto, pulsante **Connect** in alto. Ci sono tre modi:

| Modo | Host e porta | Utente | Da usare per |
|---|---|---|---|
| Connessione diretta | `db.<PROJECT-REF>.supabase.co:5432` | `postgres` | Funziona solo su reti **IPv6**: molte reti di casa e della scuola non lo sono. Da evitare |
| **Pooler, session mode** | `aws-<N>-<REGIONE>.pooler.supabase.com:5432` | `<utente>.<PROJECT-REF>` | **Da usare per tutto**: Spring Boot, script di caricamento, Power BI, DBeaver. Funziona su IPv4 |
| Pooler, transaction mode | stesso host, porta `6543` | `<utente>.<PROJECT-REF>` | Per funzioni serverless, non ci serve |

Note:
- Copiare l'host **esatto** dal pannello: il numero `<N>` non si può indovinare.
- Con il pooler, il nome utente ha sempre il suffisso `.<PROJECT-REF>` (es. `postgres.abcdefghij`).
- Il database si chiama `postgres`.
- La connessione deve essere cifrata: `sslmode=require`.

## 4. Creare le tabelle

Il modo più semplice: nel pannello, **SQL Editor** → nuova query → incollare ed eseguire, **in questo ordine**:

1. `db/schema.sql`
2. `db/dati_base.sql`
3. `db/viste_kpi.sql`

In alternativa con un client come DBeaver o `psql`, usando i dati del punto 3.

Le nostre tabelle stanno nello schema `arcade`, non in `public`: così **non sono esposte** dalle API automatiche di Supabase, che non usiamo.

> Prima provare gli script in locale con Docker: su Supabase si eseguono solo versioni già funzionanti.

## 5. Utenti del database (non usare `postgres` per tutto)

L'utente `postgres` può fare tutto, anche cancellare il database. Ognuno usa un utente con i permessi minimi. Da eseguire nello SQL Editor, scegliendo password robuste:

```sql
-- BID: API e script di caricamento (lettura e scrittura)
CREATE ROLE bid_app LOGIN PASSWORD '<password-bid>';
GRANT USAGE ON SCHEMA arcade TO bid_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA arcade TO bid_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA arcade TO bid_app;

-- BAD: Power BI (solo lettura)
CREATE ROLE bad_powerbi LOGIN PASSWORD '<password-bad>';
GRANT USAGE ON SCHEMA arcade TO bad_powerbi;
GRANT SELECT ON ALL TABLES IN SCHEMA arcade TO bad_powerbi;

-- Le tabelle e viste create in futuro ricevono gli stessi permessi
ALTER DEFAULT PRIVILEGES IN SCHEMA arcade
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO bid_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA arcade
    GRANT USAGE ON SEQUENCES TO bid_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA arcade
    GRANT SELECT ON TABLES TO bad_powerbi;
```

Con il pooler ci si collega come `bid_app.<PROJECT-REF>` e `bad_powerbi.<PROJECT-REF>`.

Da valutare: dare a `bad_powerbi` solo le viste dei KPI e non le tabelle con dati personali (email dei contatti, referenti).

## 5b. Collegarsi per la prima volta (ogni membro BID)

**Il responsabile DB**, una volta sola:
1. Invita i membri nell'organizzazione Supabase (impostazioni dell'organizzazione → **Team** → **Invite**).
2. Manda a ciascuno, **in privato**, l'host del Session pooler e la password di `bid_app`. A BAD manda solo la password di `bad_powerbi`.

**Ogni membro**, sul proprio PC:
1. Accetta l'invito ricevuto per email.
2. Installa **DBeaver Community** da [dbeaver.io](https://dbeaver.io).
3. Nuova connessione → **PostgreSQL**:
   - Host: quello ricevuto
   - Port: `5432`
   - Database: `postgres`
   - Username: `bid_app.<PROJECT-REF>`
   - Password: quella ricevuta
4. **Test Connection** (scaricare i driver se richiesto) → deve comparire "Connected".
5. Le tabelle sono in: connessione → Databases → postgres → Schemas → `arcade` → Tables.

Controllo dell'installazione (deve dare "trovati" = "attesi" su ogni riga):

```sql
SELECT 'tabelle' AS cosa, count(*) AS trovati, 22 AS attesi
  FROM information_schema.tables WHERE table_schema = 'arcade' AND table_type = 'BASE TABLE'
UNION ALL SELECT 'viste', count(*), 13 FROM information_schema.views WHERE table_schema = 'arcade'
UNION ALL SELECT 'edizioni', count(*), 3 FROM arcade.edizione
UNION ALL SELECT 'varchi', count(*), 4 FROM arcade.varco
UNION ALL SELECT 'tipi biglietto', count(*), 8 FROM arcade.tipo_biglietto
UNION ALL SELECT 'province', count(*), 21 FROM arcade.provincia
UNION ALL SELECT 'alias province', count(*), 42 FROM arcade.provincia_alias;
```

## 6. Collegare Spring Boot

In `application.properties` i dati sensibili arrivano da **variabili d'ambiente**, mai scritti nel file:

```properties
spring.datasource.url=jdbc:postgresql://${DB_HOST}:5432/postgres?sslmode=require
spring.datasource.username=${DB_USER}
spring.datasource.password=${DB_PASSWORD}
# Il piano gratuito ha poche connessioni: pool piccolo
spring.datasource.hikari.maximum-pool-size=5
```

In locale le variabili si mettono in un file `.env` (già escluso da Git nel `.gitignore`) o nella configurazione di avvio dell'IDE.

## 7. Collegare Power BI (BAD)

Power BI Desktop → **Recupera dati** → **Database PostgreSQL**:
- Server: `aws-<N>-<REGIONE>.pooler.supabase.com:5432`
- Database: `postgres`
- Credenziali: **Database**, utente `bad_powerbi.<PROJECT-REF>`

Se compare un **errore di certificato**: scaricare il certificato del server dalle impostazioni del database di Supabase e installarlo in Windows tra le "Autorità di certificazione radice attendibili", poi riprovare.

## 8. Regole d'uso

- **Pausa per inattività**: dopo 7 giorni senza attività il progetto va in pausa. I dati restano, ma il database è spento finché qualcuno non lo riattiva dal pannello. Attenzione nelle settimane di lavoro autonomo (16 novembre - 4 dicembre) e **controllare che sia attivo il giorno prima di ogni SAL e della demo finale**.
- **Password**: mai su Git, nella wiki, nelle chat di gruppo. Se una password finisce in un posto sbagliato, cambiarla subito.
- **Ricostruibile**: tutto il database deve potersi ricreare da zero con gli script in `db/` e gli script di caricamento. Così un problema su Supabase non fa perdere il lavoro.
- **Prima in locale, poi su Supabase**: ogni modifica allo schema si prova in Docker prima di eseguirla sul database condiviso.
