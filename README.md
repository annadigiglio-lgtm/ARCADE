# ARCADE Milano

Progetto Laboratorio Integrato BAD + BID — ITS ICT Piemonte, 2026.

Piattaforma per Factory Studios: gestione della vendita di spazi e sponsorizzazioni e Business Intelligence per il festival ARCADE Milano.

## Struttura del repository

| Cartella            | Contenuto                       |
| ------------------- | ------------------------------- |
| `docs/`           | Documentazione di progetto (wiki in [`docs/wiki/`](docs/wiki/README.md)) |
| `data/`           | Dati forniti dal cliente        |
| `db/`             | Schema dati PostgreSQL e script |
| `api/`            | REST API Java/Spring Boot       |
| `web/`            | Interfacce web                  |
| `power-platform/` | Soluzione Power Platform        |

## Avviare la prima demo locale

**Yassin e Daniel: iniziare dalla [guida ambiente di sviluppo](docs/wiki/ambiente-sviluppo.md).**
Include strumenti da installare, clone, configurazione privata Supabase, avvio
con Docker o Java, lavoro su API e pagine e verifica prima della pubblicazione.

API Spring Boot e pagine staff/espositore: istruzioni in [`api/README.md`](api/README.md).
Il flusso commerciale da concordare con BAD è descritto in
[`power-platform/README.md`](power-platform/README.md).

## Avvio e condivisione con Docker

Il repository include `Dockerfile`, `compose.yaml` e un file ambiente di esempio.
Istruzioni per avvio sul PC, accesso del gruppo e database:
[`docs/wiki/docker.md`](docs/wiki/docker.md).
Build Docker e cinque test Java superati. Il container di prova usa Supabase ed
è disponibile su **http://localhost:8081**. Viste API pubblicate su Supabase;
verificati i tre login, tutti i quattro endpoint staff, visite e riepilogo
espositori, ruoli e isolamento tra i due account.

Per avviare o controllare Docker dalla cartella `ARCADE`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File avvia-docker.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File avvia-docker.ps1 -Azione stato
```

Accesso del gruppo da casa: **https://arcade-milano.onrender.com**, su Render
**Free** e database Supabase. Verifica HTTPS completata: tre login, quattro
endpoint staff, visite e riepilogo espositori, ruoli e isolamento degli account.
Configurazione e aggiornamenti in [`docs/wiki/render.md`](docs/wiki/render.md).

## Team

Prossimo SAL: **4 dicembre 2026**, aggiornamento ricevuto il 9/11.
[Programma](docs/wiki/programma.md), [verifica BAD](docs/wiki/verifica-bad-2026-11-09.md)
e [import commerciale](power-platform/README.md).
I materiali della presentazione del 6 novembre vanno ripristinati nella copia locale.

- BID: Anna Digiglio, Daniel Quattrone, Yassin En Naour
- BAD: Alessandro Terlingo, Cristian Provenzano, Lorenzo Musto, Adam Nekkouss, Durand Yenje Boum
