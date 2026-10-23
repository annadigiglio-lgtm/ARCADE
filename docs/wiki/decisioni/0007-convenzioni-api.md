# 0007. Convenzioni tra DB, API e web

- **Data:** 2026-10-23
- **Stato:** accettata
- **Chi ha deciso:** BID (Anna, Yassin)

## Contesto

Prima del SAL 1 (2026-10-30) va congelato il contratto API. Servono regole comuni su quali dati l'API legge, in che formato li restituisce, come protegge i dati degli espositori e come si mostra il "tempo reale" in una demo che si svolge quando la fiera non è in corso.

## Decisione

| Tema | Regola |
|---|---|
| Fonte dei numeri | L'API legge solo le viste e le funzioni di `db/viste_api.sql` e `db/viste_kpi.sql`, senza ricalcolare ([viste-api.md](../viste-api.md)) |
| JSON | Nomi in `camelCase`; date in ISO 8601 con fuso (`2025-12-20T11:55:00+01:00`); importi come numeri; percentuali come frazione (`0.708`). La formattazione la fa il web |
| Autenticazione | Login con JWT (Spring Security); il token contiene `ruolo` e `idEspositore`; password salvate in BCrypt |
| Isolamento espositori | L'`idEspositore` si prende **sempre dal token**; gli URL usano `/espositore/me/...`, mai un id |
| Tempo reale | Il cruscotto chiede i dati **ogni 30 secondi** (polling) |
| Demo | L'"ora attuale" la decide l'API con un'impostazione (es. `arcade.demo.inizio=2025-12-20T10:00` e una velocità); le funzioni del cruscotto ricevono l'istante come parametro |
| Paginazione | Solo dove serve (contatti), con i parametri standard di Spring `?page=0&size=50` |
| JPA | Le tabelle si creano solo con gli script SQL: `spring.jpa.hibernate.ddl-auto=validate`; le viste sono entità di sola lettura (`@Immutable`); le funzioni si chiamano con query native |
| Database per lo sviluppo API | Supabase con l'utente `bid_app` (l'API legge soltanto); il database locale è facoltativo |

## Perché

- Una sola fonte per i numeri: cruscotto, portale e Power BI danno gli stessi valori.
- Il polling è il metodo più semplice e funziona con qualunque tecnologia del frontend; le presenze cambiano nell'arco di minuti.
- Con l'istante come parametro la demo "rivede" una giornata vera del 2025 come se fosse in diretta, senza dati inventati.
- Prendere l'id dal token impedisce a un espositore di leggere i dati di un altro cambiando l'URL.

## Conseguenze

- Le funzioni del cruscotto devono rispondere in pochi secondi (oggi 0,4-1,3 s in locale).
- Servono utenti di demo nel database: almeno uno staff e due espositori.
