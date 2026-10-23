# Team e ruoli

## Composizione (Gruppo 5)

| Team          | Membri                                                                                    |
| ------------- | ----------------------------------------------------------------------------------------- |
| **BID** | Anna Digiglio, Daniel Quattrone, Yassin En Naour                                          |
| **BAD** | Alessandro Terlingo, Cristian Provenzano, Lorenzo Musto, Adam Nekkouss, Durand Yenje Boum |

Team leader: _da definire_

## Responsabilità secondo il documento di progetto

### BID: piattaforma dati e BI in codice

- Acquisizione (caricamento e pulizia) di **biglietteria, tornelli e scanner**
- **Schema dati PostgreSQL**: progettazione e alimentazione del modello dati condiviso
- **REST API** in Java / Spring Boot
- **Cruscotto operativo** per lo staff (affluenza in tempo reale)
- **Portale essenziale** per gli espositori

### BAD: gestione commerciale e BI direzionale

- **Back-office Power Apps**: listino, planimetria, contratti, acconti, prelazione
- **Flussi Power Automate**
- **Report Power BI** per la direzione
- **App di scansione** allo stand
- **Fornitura dei dati commerciali** al modello dati condiviso

### Zone di collaborazione

- Modello dati (lo progetta BID, BAD ci porta i dati commerciali)
- Definizione dei KPI (devono dare gli stessi numeri in Power BI e nelle pagine web)
- Integrazione Power Apps / Power Automate con il DB o le API
- Formato delle scansioni inviate dall'app di BAD

Vedi [architettura.md](architettura.md) per lo schema completo.

## Divisione interna BID

| Area      | Responsabile | Contenuto                                                         |
| --------- | ------------ | ----------------------------------------------------------------- |
| DB ed ETL | Anna         | Schema, script di caricamento, registro anomalie, anonimizzazione |
| API       | Yassin       | Contratto OpenAPI, Spring Boot, autenticazione e ruoli            |
| Web       | Daniel       | Cruscotto staff, portale espositori                               |

Ognuno ha un'area principale ma tutti devono saper spiegare tutto: si fanno revisioni incrociate del codice.

### Come si incastrano le aree

```
PostgreSQL (Supabase)  ──►  API Spring Boot  ──►  Pagine web
      ANNA                      YASSIN               DANIEL
 dati puliti + KPI         espone i dati         li mostra a staff
   nelle viste SQL         e controlla chi       ed espositori
                           può vedere cosa
```

Regola di fondo: **i numeri si calcolano una volta sola, nel DB** ([decisione 0003](decisioni/0003-kpi-in-viste-sql.md)). Le API non ricalcolano nulla e il web non fa conti in JavaScript: così cruscotto, portale e Power BI di BAD danno gli stessi valori.

Scadenze di riferimento ([programma.md](programma.md)): **SAL 1 30/10** (schema e contratto API congelati), **SAL 2 13/11** (due edizioni caricate e un contratto 2026 venduto), **finale 04/12** (demo prima, durante, dopo).

### Anna: DB ed ETL

Responsabile di tutto ciò che sta dentro PostgreSQL: struttura delle tabelle, ingresso dei dati, uscita dei dati puliti.

Già fatto: analisi dati e registro anomalie, `schema.sql`, viste KPI, script in `db/caricamento/`, storico 2024-2025 caricato (28/28 controlli OK), Supabase configurato.

**Entro il SAL 1**

- Rivedere lo schema con BAD e congelarlo; diagramma ER per la presentazione
- Cambiare le password di `bid_app` e `bad_powerbi` e consegnarle in privato (`bid_app` a Yassin e Daniel, `bad_powerbi` a BAD)
- Concordare con Yassin nomi e colonne delle viste lette dalle API
- Velocizzare le viste delle presenze stimate (~6 s oggi)
- Decidere se i dati del cliente stanno su Git o fuori

**Entro il SAL 2**

- Anonimizzazione: niente nomi ed email esposti dove non servono; per i minori solo dati aggregati
- Mappatura colonne Dataverse ↔ PostgreSQL con BAD e caricamento dell'export commerciale (opzione B), così il contratto 2026 venduto in Power Apps compare nel DB

**Entro la finale**

- Script di simulazione dei passaggi ai varchi e delle scansioni agli stand per la demo in tempo reale
- Ingresso delle scansioni dell'app di BAD
- Verifica che web e Power BI diano gli stessi numeri

### Yassin: API

Responsabile dello strato in mezzo: il servizio Java che legge dal DB, risponde al web e decide chi può vedere cosa.

**Entro il SAL 1 (la parte più urgente di BID)**

- Contratto OpenAPI (file YAML in `api/`): endpoint, parametri, formato delle risposte. Dopo il SAL 1 non si cambia. Esempi:
  - `POST /auth/login`
  - `GET /affluenza/padiglioni`: presenze attuali per padiglione (staff)
  - `GET /kpi/...`: KPI letti dalle viste
  - `GET /espositore/me/visite`, `/espositore/me/riepilogo`, `/espositore/me/confronto` (espositore)
- Input necessari: da Daniel cosa mostra ogni pagina, da Anna quali viste esistono

**Entro il SAL 2**

- Progetto Spring Boot in `api/`, collegato a Supabase con `bid_app`
- Endpoint principali funzionanti, che leggono le viste senza ricalcolare
- Autenticazione e ruoli: login, token (es. JWT), almeno `STAFF` ed `ESPOSITORE`

**Entro la finale**

- Isolamento espositori: l'id dell'espositore si ricava **dal token, mai da un parametro dell'URL**
- Aggiornamento in tempo reale per il cruscotto (polling o Server-Sent Events, da decidere con Daniel)
- Se il tutor lo consente, job di lettura automatica da Dataverse (opzione A, vedi [architettura.md](architettura.md#sincronizzazione-dataverse--postgresql))

### Daniel: Web

Responsabile di ciò che vedono le persone: due pagine per due pubblici diversi.

**Entro il SAL 1**

- Wireframe delle due pagine con l'elenco dei dati necessari in ciascuna, da passare subito a Yassin per il contratto API
- Scelta della tecnologia del frontend, da registrare in `decisioni/`

**Entro il SAL 2**

- **Cruscotto staff** (schermo in fiera): presenze attuali per padiglione, andamento della giornata, ingressi, avvisi di affollamento; leggibile da lontano
- **Portale espositori**: login e visite al proprio stand per giorno e ora
- Finché le API non sono pronte si lavora con dati finti ricavati dal contratto OpenAPI

**Entro la finale**

- Aggiornamento automatico del cruscotto
- Portale completo: riepilogo di fine fiera, confronto 2024/2025, invito al rinnovo
- Nessun dato personale o di minori nelle pagine

### Passaggi di consegna tra le aree

| Tra             | Cosa si accordano                                                        | Quando          |
| --------------- | ------------------------------------------------------------------------ | --------------- |
| Anna → Yassin   | Nomi e colonne delle viste                                               | Entro il 26/10  |
| Daniel → Yassin | Contenuto di ogni pagina (wireframe)                                     | Entro il 26/10  |
| Yassin → Daniel | Contratto OpenAPI                                                        | Prima del 30/10 |
| Daniel → Anna   | Se manca un numero si aggiunge una vista nel DB, non si calcola nel web | Sempre          |

### Compiti di tutti

- Collegarsi al DB con DBeaver o pgAdmin ([guida](guida-supabase.md))
- Revisioni incrociate del codice: chiunque può essere interrogato su qualunque riga
- Riunione con BAD sui KPI e preparazione della presentazione del SAL 1

## Contatti

| Chi                | Ruolo   | Email           |
| ------------------ | ------- | --------------- |
| Paolo Ghirlinzoni  | Cliente | _da chiedere_ |
| Emanuele Campanini | Cliente | _da chiedere_ |
| Tutor              |         | _da chiedere_ |
