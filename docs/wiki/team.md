# Team e ruoli

## Composizione (Gruppo 5)

| Team | Membri |
|---|---|
| **BID** | Anna Digiglio, Daniel Quattrone, Yassin En Naour |
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

## Divisione interna BID (proposta)

| Area | Responsabile | Contenuto |
|---|---|---|
| DB ed ETL | _da assegnare_ | Schema, script di caricamento, registro anomalie, anonimizzazione |
| API | _da assegnare_ | Contratto OpenAPI, Spring Boot, autenticazione e ruoli |
| Web | _da assegnare_ | Cruscotto staff, portale espositori |

Ognuno ha un'area principale ma tutti devono saper spiegare tutto: si fanno revisioni incrociate del codice.

## Contatti

| Chi | Ruolo | Email |
|---|---|---|
| Paolo Ghirlinzoni | Cliente | _da chiedere_ |
| Emanuele Campanini | Cliente | _da chiedere_ |
| Tutor | | _da chiedere_ |
