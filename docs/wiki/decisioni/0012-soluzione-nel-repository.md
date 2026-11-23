# 0012. Soluzione Power Platform conservata nel repository con pac

- **Data:** 2026-11-06
- **Stato:** proposta
- **Chi ha deciso:** BAD

## Contesto

La soluzione ARCADE BAD vive nell'ambiente Developer, che non è gestito: questi ambienti vengono sospesi dal 2026-12-15 e cancellati dal 2027-01-15. Serve una copia della soluzione con lo storico delle versioni. Power Platform ha un collegamento diretto a Git (Soluzioni → Connetti a Git), che funziona solo con gli ambienti gestiti (Managed Environments).

## Opzioni considerate

- **Collegamento a Git integrato:** automatico; richiede un ambiente gestito, non compreso nel piano Developer.
- **Export con `pac solution export` e `unpack`, poi commit in questo repository:** due comandi a ogni versione; funziona con il nostro ambiente.
- **Repository separato su Azure DevOps:** gratuito fino a 5 utenti Basic; il codice di BID resterebbe su GitHub, quindi avremmo due repository da allineare.

## Decisione

A ogni versione importante la soluzione si esporta (non gestita), si scompatta in `power-platform/solution/ARCADEBAD/` e si fa il commit in questo repository, su un branch con pull request.

## Perché

- Un solo repository per BID e BAD, come richiesto dalla consegna.
- I file scompattati mostrano cosa è cambiato in tabelle, app e flussi.

## Conseguenze

- Il dettaglio dei comandi è in [`power-platform/README_STATO_BAD.md`](../../../power-platform/README_STATO_BAD.md).
- Prima del 2026-12-15 va fatto un export finale, anche dei dati.
